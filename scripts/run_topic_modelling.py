import mlflow
import os
import pandas as pd
from src.data.topic_modelling import (
    train_bertopic_model, print_top_keywords, reduce_topics,
    calculate_coherence_score, save_visualizations
)

def find_optimal_configuration(titles, embedding_models=None, topic_numbers=None):
    if embedding_models is None:
        embedding_models = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]
    
    if topic_numbers is None:
        topic_numbers = [10, 15, 20, 25, 30]
    
    results = []
    
    for emb_model in embedding_models:
        model, topics = train_bertopic_model(titles, embedding_model_name=emb_model)
        
        for n_topics in topic_numbers:
            print(f"Testing {emb_model} with {n_topics} topics")
            reduced_model = reduce_topics(model, titles, nr_topics=n_topics)
            
            tokenized_titles = [title.split() for title in titles]
            coherence = calculate_coherence_score(reduced_model, tokenized_titles)
            
            results.append({
                "embedding_model": emb_model,
                "n_topics": n_topics,
                "coherence": coherence
            })
            
            print(f"Coherence: {coherence}")
    
    # Find best configuration
    best_result = max(results, key=lambda x: x["coherence"])
    print(f"Best configuration: {best_result}")
    
    return results, best_result

def main():
    mlflow.set_experiment("Prism Lens")
    
    with mlflow.start_run():
        # Log parameters
        sample_size = 5000
        mlflow.log_param("sample_size", sample_size)
        
        # Load data
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dari scripts/
        csv_path = os.path.join(BASE_DIR, "data", "processed", "arxiv_papers_cleaned.csv")
        df = pd.read_csv(csv_path)

        if len(df) > sample_size:
            df = df.sample(sample_size, random_state=42)
        
        titles = df["title"].dropna().tolist()
        
        # Experiment with different configurations
        embedding_models = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]
        topic_numbers = [10, 15, 20, 25, 30]
        mlflow.log_param("embedding_models", embedding_models)
        mlflow.log_param("topic_numbers", topic_numbers)
        
        results, best_result = find_optimal_configuration(titles, embedding_models, topic_numbers)
        
        # Log results and best configuration
        for result in results:
            mlflow.log_metric(f"coherence_{result['embedding_model']}_{result['n_topics']}", result["coherence"])
        
        mlflow.log_param("best_embedding_model", best_result["embedding_model"])
        mlflow.log_param("best_n_topics", best_result["n_topics"])
        mlflow.log_metric("best_coherence", best_result["coherence"])
        
        # Train and save the best model
        best_model, _ = train_bertopic_model(titles, embedding_model_name=best_result["embedding_model"])
        best_model = reduce_topics(best_model, titles, nr_topics=best_result["n_topics"])
        
        # Ensure save directory exists
        save_path = '../data/bertopic_model_best'
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save the model
        best_model.save(save_path)
        mlflow.log_artifact(save_path, artifact_path="models")
        
        # Save visualizations for the best model
        save_visualizations(best_model, output_dir="../data/plots", one_by_one=True)
        mlflow.log_artifacts("../data/plots", artifact_path="visualizations")
        
        print("Optimal topic modeling completed successfully!")

if __name__ == "__main__":
    main()
