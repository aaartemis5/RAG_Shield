import pandas as pd

# Load the Cybersecurity CSV file.
df = pd.read_csv("Cybersecurity_Dataset.csv")

# Inspect the dataset (optional)
print("Dataset columns:", df.columns)
print(df.head())

# Create a detailed prompt that combines multiple columns.
# Adjust column names as necessary to match your CSV headers.
df['prompt'] = (
    "Threat Actor: " + df['Threat Actor'].astype(str) + ". " +
    "Attack Vector: " + df['Attack Vector'].astype(str) + ". " +
    "Geographical Location: " + df['Geographical Location'].astype(str) + ". " +
    "IOCs: " + df['IOCs (Indicators of Compromise)'].astype(str) + ". " +
    "Sentiment in Forums: " + df['Sentiment in Forums'].astype(str) + ". " +
    "Severity Score: " + df['Severity Score'].astype(str) + "."
)

# Create a richer, multi-sentence completion by combining additional details.
# Instead of using just 'Threat Category', we append it with a description.
df['completion'] = (
    "Threat Category: " + df['Threat Category'].astype(str) + ". " +
    "This threat involves a sophisticated attack where the listed attributes indicate a multi-vector intrusion. " +
    "Review the provided details carefully to understand the potential impact and mitigation measures."
)

# Now, we want to create a balanced sample of up to 400 examples.
# Use stratified sampling based on the 'completion' field.
classes = df['completion'].unique()
samples_per_class = 400 // len(classes) if len(classes) > 0 else 400

sampled_dfs = []
for cls in classes:
    class_df = df[df['completion'] == cls]
    n_samples = min(len(class_df), samples_per_class)
    sampled_df = class_df.sample(n=n_samples, random_state=42)
    sampled_dfs.append(sampled_df)

# Combine the samples and shuffle.
if sampled_dfs:
    balanced_df = pd.concat(sampled_dfs).sample(frac=1, random_state=42).reset_index(drop=True)
else:
    balanced_df = df.sample(n=400, random_state=42).reset_index(drop=True)

# If total samples are less than 400, add random examples until reaching 400.
if len(balanced_df) < 400:
    remaining = df.drop(balanced_df.index)
    additional_samples = remaining.sample(n=400 - len(balanced_df), random_state=42)
    balanced_df = pd.concat([balanced_df, additional_samples]).sample(frac=1, random_state=42).reset_index(drop=True)

# Keep only the columns needed for fine-tuning.
finetune_df = balanced_df[['prompt', 'completion']]

# Save to CSV.
finetune_df.to_csv("finetune_dataset.csv", index=False)
print(f"Balanced fine-tuning dataset saved as 'finetune_dataset.csv' with {len(finetune_df)} examples.")
