from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
import os
import gc


def tokenize_titles(titles):
    return [t.lower().strip().split() for t in titles if isinstance(t, str)]


def train_bertopic_model(titles, embedding_model_name="all-MiniLM-L6-v2"):
    print(f"Loading embedding model: {embedding_model_name}")
    embedding_model = SentenceTransformer(embedding_model_name)

    topic_model = BERTopic(
        embedding_model=embedding_model,
        verbose=True,
        calculate_probabilities=False,
        n_gram_range=(1, 2)
    )

    topics, _ = topic_model.fit_transform(titles)
    gc.collect()
    return topic_model, topics


def reduce_topics(topic_model, titles, nr_topics=10):
    print(f"Reducing to {nr_topics} topics...")
    try:
        topic_model.reduce_topics(titles, nr_topics=nr_topics, n_iter=10)
    except Exception as e:
        print(f"Warning: Topic reduction encountered an issue: {e}")
    return topic_model


def calculate_coherence_score(topic_model, tokenized_titles):
    try:
        topics = topic_model.get_topics()
        topic_words = [[word for word, _ in words] for tid, words in topics.items() if tid != -1]
        if not topic_words:
            return 0.0

        dictionary = Dictionary(tokenized_titles)
        corpus = [dictionary.doc2bow(text) for text in tokenized_titles]

        coherence_model = CoherenceModel(
            topics=topic_words,
            texts=tokenized_titles,
            corpus=corpus,
            dictionary=dictionary,
            coherence='c_v'
        )

        score = coherence_model.get_coherence()
        del dictionary, corpus, coherence_model
        gc.collect()
        return score
    except Exception as e:
        print(f"Warning: Coherence calculation failed: {e}")
        return 0.0


def save_visualizations(model, output_dir="../data/plots", one_by_one=True):
    os.makedirs(output_dir, exist_ok=True)
    try:
        model.visualize_topics().write_html(f"{output_dir}/topics_visualized.html")
        model.visualize_barchart(top_n_topics=20).write_html(f"{output_dir}/topics_barchart.html")
        model.visualize_hierarchy().write_html(f"{output_dir}/topics_hierarchy.html")
        gc.collect()
    except Exception as e:
        print(f"Warning: Visualization failed: {e}")