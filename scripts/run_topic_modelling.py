import mlflow
import os
import pandas as pd
import sys
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.topic_modelling import (
    train_bertopic_model,
    reduce_topics,
    calculate_coherence_score,
    save_visualizations
)


def tokenize_titles(titles):
    return [title.split() for title in titles]


def find_optimal_configuration(titles, tokenized_titles, embedding_models, topic_numbers):
    results = []

    for emb_model in embedding_models:
        print(f"\nTrying embedding model: {emb_model}")
        model, _ = train_bertopic_model(titles, embedding_model_name=emb_model)

        for n_topics in topic_numbers:
            print(f"→ Reducing to {n_topics} topics...")
            reduced_model = reduce_topics(model, titles, nr_topics=n_topics)

            coherence = calculate_coherence_score(reduced_model, tokenized_titles)
            print(f"Coherence for {emb_model} @ {n_topics} topics: {coherence:.4f}")

            results.append({
                "embedding_model": emb_model,
                "n_topics": n_topics,
                "coherence": coherence
            })

    best_result = max(results, key=lambda x: x["coherence"])
    print(f"\nBest configuration: {best_result}")

    return results, best_result


def enrich_with_topics(final_model, titles, df, BASE_DIR):
    # Assign topic IDs and probabilities
    topics, probs = final_model.transform(titles)
    df["topic_id"] = topics
    df["probability"] = probs

    # Assign human-readable topic labels
    def get_label(topic_id):
        if topic_id == -1:
            return "Other"
        words = final_model.get_topic(topic_id)
        return ", ".join([w[0] for w in words[:5]]) if words else "Other"

    df["topic_name"] = df["topic_id"].apply(get_label)

    # Save the enriched DataFrame
    topic_csv_path = os.path.join(BASE_DIR, "data", "processed", "arxiv_with_topics.csv")
    df.to_csv(topic_csv_path, index=False)
    print(f"Saved enriched metadata (based on Title) to: {topic_csv_path}")


def main():
    mlflow.set_experiment("Prism Lens")

    with mlflow.start_run():
        # === Load Dataset ===
        sample_size = 5000
        mlflow.log_param("sample_size", sample_size)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(BASE_DIR, "data", "processed", "arxiv_papers_cleaned.csv")
        df = pd.read_csv(csv_path)

        df = df[df["title"].notna()]
        if len(df) > sample_size:
            df = df.sample(sample_size, random_state=42)

        titles = df["title"].tolist()
        tokenized_titles = tokenize_titles(titles)

        # === Define Configs ===
        embedding_models = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]
        topic_numbers = [10, 15, 20, 25, 30]
        mlflow.log_param("embedding_models", embedding_models)
        mlflow.log_param("topic_numbers", topic_numbers)

        # === Search Best Config ===
        results, best = find_optimal_configuration(titles, tokenized_titles, embedding_models, topic_numbers)

        for res in results:
            metric_name = f"coherence_{res['embedding_model']}_{res['n_topics']}"
            mlflow.log_metric(metric_name, res["coherence"])

        mlflow.log_param("best_embedding_model", best["embedding_model"])
        mlflow.log_param("best_n_topics", best["n_topics"])
        mlflow.log_metric("best_coherence", best["coherence"])

        # === Final Training & Metadata Enrichment ===
        final_model, _ = train_bertopic_model(titles, embedding_model_name=best["embedding_model"])
        final_model = reduce_topics(final_model, titles, nr_topics=best["n_topics"])

        enrich_with_topics(final_model, titles, df, BASE_DIR)
        
        # === Save Model & Visualizations ===
        # Fix: Add the .pkl extension directly to the save path
        save_path = os.path.join(BASE_DIR, "data", "bertopic_model_best.pkl")
        save_dir = os.path.dirname(save_path)

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        final_model.save(save_path)  # Now saves directly as a .pkl file
        mlflow.log_artifact(save_path, artifact_path="models") 

        plots_dir = os.path.join(BASE_DIR, "data", "plots")
        save_visualizations(final_model, output_dir=plots_dir)
        mlflow.log_artifacts(plots_dir, artifact_path="visualizations")

        print("\nDone! Topic modeling pipeline completed successfully.")

if __name__ == "__main__":
    main()