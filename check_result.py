import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.utils.multiclass import unique_labels

# Load data
correctfile = 'data/train/external_parties_train.csv'  # transaction_reference_id, external_id
checkfile = './merged_result.csv'  # transaction_reference_id, external_id

correctdf = pd.read_csv(correctfile)
checkdf = pd.read_csv(checkfile)

# Keep only necessary columns
correctdf = correctdf[['transaction_reference_id', 'external_id']]
checkdf = checkdf[['transaction_reference_id', 'external_id']]
#Precision: The proportion of correctly identified pairs of external parties that are truly the same entity.
#Recall: The proportion of all actual pairs of external parties that represent the same entity and are correctly identified.
# Group clusters into dictionaries: external_id -> set of transaction_reference_id
correct_clusters = correctdf.groupby('external_id')['transaction_reference_id'].apply(set).to_dict()
check_clusters = checkdf.groupby('external_id')['transaction_reference_id'].apply(set).to_dict()

# Create a reverse map for transaction_reference_id -> external_id in correctdf
transaction_to_correct_cluster = {tid: cid for cid, tids in correct_clusters.items() for tid in tids}

# Initialize metrics
total_tp, total_fp, total_fn = 0, 0, 0

# Evaluate each cluster in checkdf
for check_id, check_tids in check_clusters.items():
    # Map each point in check cluster to its correct cluster (if exists)
    correct_cluster_ids = {transaction_to_correct_cluster.get(tid) for tid in check_tids}
    correct_cluster_ids.discard(None)  # Remove None if any points don't exist in correct clusters

    # Check if it matches a single correct cluster
    if len(correct_cluster_ids) == 1:
        correct_id = correct_cluster_ids.pop()
        correct_tids = correct_clusters[correct_id]
        
        # Calculate precision and recall for this cluster
        tp = len(check_tids & correct_tids)  # True positives
        fp = len(check_tids - correct_tids)  # False positives
        fn = len(correct_tids - check_tids)  # False negatives
    else:
        # Completely mismatched cluster
        tp, fp, fn = 0, len(check_tids), 0

    # Aggregate metrics
    total_tp += tp
    total_fp += fp
    total_fn += fn

# Calculate overall metrics
precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

# Print results
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
