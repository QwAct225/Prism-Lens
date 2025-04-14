from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
import os
import gc
from tqdm import tqdm

def train_bertopic_model(titles, embedding_model_name="all-MiniLM-L6-v2"):
    # Use smaller embedding model to save memory
    print(f"Loading embedding model: {embedding_model_name}")
    embedding_model = SentenceTransformer(embedding_model_name)
    
    # Create BERTopic model with memory optimization
    topic_model = BERTopic(
        embedding_model=embedding_model,
        verbose=True,
        calculate_probabilities=False,  # Save memory
        n_gram_range=(1, 2)  # Limit to unigrams and bigrams
    )
    
    # Process in batches for large datasets
    batch_size = 1000
    if len(titles) > batch_size:
        all_topics = []
        for i in tqdm(range(0, len(titles), batch_size)):
            batch = titles[i:i+batch_size]
            if i == 0:
                # First batch: fit the model
                topics, _ = topic_model.fit_transform(batch)
            else:
                # Subsequent batches: transform only
                topics, _ = topic_model.transform(batch)
            all_topics.extend(topics)
        topics = all_topics
    else:
        # Small dataset: process all at once
        topics, _ = topic_model.fit_transform(titles)
    
    # Clear memory
    gc.collect()
    
    return topic_model, topics

def print_top_keywords(topic_model, n_topics=10):
    topics = topic_model.get_topics()
    
    # Sort topics by size (excluding -1 which is the outlier topic)
    topic_sizes = topic_model.get_topic_freq()
    sorted_topics = [x[0] for x in topic_sizes.iterrows() if x[1]['Topic'] != -1][:n_topics]
    
    for topic_num in sorted_topics:
        if topic_num in topics:
            words = topics[topic_num]
            print(f"Topic {topic_num}: {[word[0] for word in words[:10]]}")

def reduce_topics(topic_model, titles, nr_topics=10):
    print(f"Reducing to {nr_topics} topics...")
    try:
        # Set a maximum number of iterations to prevent infinite loops
        topic_model.reduce_topics(titles, nr_topics=nr_topics, n_iter=10)
    except Exception as e:
        print(f"Warning: Topic reduction encountered an issue: {e}")
        print("Continuing with original topics")
    return topic_model

def save_visualizations(model, output_dir="../data/plots", one_by_one=True):
    os.makedirs(output_dir, exist_ok=True)
    
    if one_by_one:
        # Generate visualizations one at a time to manage memory
        try:
            print("Generating topic scatter plot...")
            model.visualize_topics().write_html(f"{output_dir}/topics_visualized.html")
            gc.collect()  # Free memory
            
            print("Generating barchart visualization...")
            model.visualize_barchart(top_n_topics=20).write_html(f"{output_dir}/topics_barchart.html")
            gc.collect()  # Free memory
            
            print("Generating hierarchy visualization...")
            model.visualize_hierarchy().write_html(f"{output_dir}/topics_hierarchy.html")
            gc.collect()  # Free memory
        except Exception as e:
            print(f"Warning: Visualization failed: {e}")
            print("Continuing with remaining processing")
    else:
        # Generate all visualizations at once (original behavior)
        model.visualize_topics().write_html(f"{output_dir}/topics_visualized.html")
        model.visualize_barchart(top_n_topics=20).write_html(f"{output_dir}/topics_barchart.html")
        model.visualize_hierarchy().write_html(f"{output_dir}/topics_hierarchy.html")

def calculate_coherence_score(topic_model, cleaned_tokenized_titles):
    try:
        # Extract keywords per topic
        topics = topic_model.get_topics()
        topic_words = [[word for word, _ in words] for topic_id, words in topics.items() if topic_id != -1]
        
        if not topic_words:
            print("No valid topics found for coherence calculation")
            return 0.0
        
        # Create dictionary and corpus
        dictionary = Dictionary(cleaned_tokenized_titles)
        corpus = [dictionary.doc2bow(text) for text in cleaned_tokenized_titles]
        
        # Calculate coherence
        coherence_model = CoherenceModel(
            topics=topic_words,
            texts=cleaned_tokenized_titles,
            corpus=corpus,
            dictionary=dictionary,
            coherence='c_v'
        )
        
        coherence_score = coherence_model.get_coherence()
        
        # Clear memory
        del dictionary, corpus, coherence_model
        gc.collect()
        
        return coherence_score
    except Exception as e:
        print(f"Warning: Coherence calculation failed: {e}")
        return 0.0