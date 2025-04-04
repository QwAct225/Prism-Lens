import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import glob


class VisualizationService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_dir = os.path.join(base_dir, "data")
        self.plots_dir = os.path.join(self.data_dir, "plots")
        self.cleaned_file = os.path.join(self.data_dir, "arxiv_papers_cleaned.csv")
        self.raw_file = os.path.join(self.data_dir, "arxiv_papers_raw.csv")
        self.embeddings_file = os.path.join(self.data_dir, "embeddings.npy")

        # Ensure all required directories exist
        os.makedirs(self.plots_dir, exist_ok=True)

    def list_plots(self) -> List[str]:
        """List all available plots"""
        if not os.path.exists(self.plots_dir):
            return []

        plot_files = glob.glob(os.path.join(self.plots_dir, "*.png"))
        return [os.path.basename(f) for f in plot_files]

    def get_plot_path(self, plot_name: str) -> str:
        """Get the file path for a specific plot"""
        return os.path.join(self.plots_dir, plot_name)

    def _load_data(self) -> pd.DataFrame:
        """Load the cleaned papers data"""
        if os.path.exists(self.cleaned_file):
            return pd.read_csv(self.cleaned_file)
        return pd.DataFrame()

    def get_papers(self, limit: int = 10, skip: int = 0,
                   search: Optional[str] = None,
                   sort_by: Optional[str] = None,
                   sort_order: Optional[str] = "asc") -> List[Dict[str, Any]]:
        """Get papers with pagination, searching, and sorting"""
        df = self._load_data()

        if df.empty:
            return []

        # Convert string representation of lists to actual lists for authors and cleaned_authors
        if "Authors" in df.columns:
            df["Authors"] = df["Authors"].apply(
                lambda x: x.split(", ") if isinstance(x, str) else []
            )

        if "cleaned_authors" in df.columns:
            df["cleaned_authors"] = df["cleaned_authors"].apply(
                lambda x: x.split(", ") if isinstance(x, str) else []
            )

        # Apply search filter if provided
        if search:
            search = search.lower()
            # Search in titles and authors
            title_mask = df["Title"].str.lower().str.contains(search, na=False)

            # For authors, need to check each author in the list
            if "Authors" in df.columns:
                authors_mask = df["Authors"].apply(
                    lambda authors: any(search in author.lower() for author in authors)
                )
                df = df[title_mask | authors_mask]
            else:
                df = df[title_mask]

        # Apply sorting if provided
        if sort_by and sort_by in df.columns:
            ascending = sort_order.lower() == "asc"
            df = df.sort_values(by=sort_by, ascending=ascending)

        # Apply pagination
        df = df.iloc[skip:skip + limit]

        # Convert to list of dictionaries
        result = []
        for _, row in df.iterrows():
            paper = {
                "title": row["Title"],
                "authors": row["Authors"] if "Authors" in row else []
            }

            if "cleaned_title" in row:
                paper["cleaned_title"] = row["cleaned_title"]

            if "cleaned_authors" in row:
                paper["cleaned_authors"] = row["cleaned_authors"]

            result.append(paper)

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the papers dataset"""
        df = self._load_data()

        if df.empty:
            return {"error": "No data available"}

        # Basic statistics
        stats = {
            "total_papers": len(df),
            "unique_authors": 0,
            "average_authors_per_paper": 0,
            "average_title_length": 0,
        }

        # Calculate unique authors
        if "Authors" in df.columns:
            # Split author strings and flatten the list
            all_authors = []
            for authors_str in df["Authors"]:
                if isinstance(authors_str, str):
                    all_authors.extend(authors_str.split(", "))

            stats["unique_authors"] = len(set(all_authors))
            stats["average_authors_per_paper"] = len(all_authors) / len(df) if len(df) > 0 else 0

        # Calculate average title length
        if "Title" in df.columns:
            stats["average_title_length"] = df["Title"].str.len().mean()

        return stats

    def get_embeddings(self, limit: int = 100, skip: int = 0) -> Dict[str, Any]:
        """Get paper embeddings for visualization"""
        if not os.path.exists(self.embeddings_file):
            return {"error": "Embeddings file not found"}

        try:
            embeddings = np.load(self.embeddings_file)
            df = self._load_data()

            if embeddings.shape[0] != len(df):
                return {"error": "Embeddings dimension mismatch with data"}

            # Apply pagination
            embeddings = embeddings[skip:skip + limit]
            df = df.iloc[skip:skip + limit]

            # Format response
            result = {
                "count": len(embeddings),
                "items": []
            }

            for i, (embedding, (_, row)) in enumerate(zip(embeddings, df.iterrows())):
                item = {
                    "paper_id": skip + i,
                    "title": row["Title"],
                    "embedding": embedding.tolist()
                }
                result["items"].append(item)

            return result

        except Exception as e:
            return {"error": f"Error loading embeddings: {str(e)}"}