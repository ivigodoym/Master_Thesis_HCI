import pandas as pd
import numpy as np
import openai

# Set pandas display options to show all rows and columns
pd.set_option('display.max_colwidth', None)

# Data Processing:
data_path = "/Users/ivannagodoymunoz/Desktop/Master Thesis/Testing"
data_chunksize = 500  # Define the chunk size
thesis_df_reader = pd.read_csv(f"{data_path}/test2_data_sample500.csv", sep=",", chunksize=data_chunksize, iterator=True)

openai.api_key = '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'

emotion_labels = ["surprised", "excited", "angry", "proud", "sad", "annoyed",
                  "grateful", "lonely", "afraid", "terrified", "guilty", "impressed",
                  "disgusted", "hopeful", "confident", "furious", "anxious", "anticipating",
                  "joyful", "nostalgic", "disappointed", "prepared", "jealous", "content",
                  "devastated", "sentimental", "embarrassed", "caring", "trusting", "ashamed",
                  "apprehensive", "faithful"]

# Iterate over the first chunk and print it
#for chunk in thesis_df_reader:
#    print(chunk)
#    break  # Stop after printing the first chunk

def process_chunk(chunky):
    conv_sample = chunky.groupby('conv_id')['utterance'].apply(list).reset_index().sort_values(by='conv_id')
    # Extract unique conversation IDs from grouped_data
    conversation_ids = conv_sample['conv_id'].tolist()
    # Extract emotion labels corresponding to the conversation IDs
    emotions_list = chunky.groupby('conv_id')['emotion_label'].unique().tolist()
    emotions_list = np.concatenate(emotions_list).tolist()
    # Create a new dataframe to store the listener responses
    responses_chunk = pd.DataFrame(columns=['conv_id', 'Test2.1_response'])

    for index, row in conv_sample.iterrows():
        conv_id = row['conv_id']
        conversation_context = chunky.loc[chunk['conv_id'] == conv_id, 'context'].iloc[0]
        # Extract emotion labels for the conversation
        emotions = chunky.loc[chunk['conv_id'] == conv_id, 'emotion_label'].tolist()
        # Selecting the most frequent emotion label for the conversation
        emotion = max(set(emotions), key=emotions.count)
        # Extract first utterance for the empathetic response
        first_utterance = row['utterance'][0]
        # Generate empathetic response
        empathetic_response = generate_empathetic_response(conversation_context, emotion, first_utterance)
        # Save the conversation ID and listener response in the dataframe
        new_row = pd.DataFrame({
            'conv_id': [conv_id],
            'Test2.1_response': [empathetic_response]
        })
        responses_chunk = pd.concat([responses_chunk, new_row], ignore_index=True)
    return responses_chunk

# Function to generate empathetic responses based on situation, emotion, and the first utterance
def generate_empathetic_response(context, emotion, first_utterance):
    prompt = f"Consider a situation and the emotion of a speaker. Situation: {context}\nEmotion: {emotion}\nAct as the listener and reply to the speaker.\nSpeaker: {first_utterance}\nListener:"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125", #Achtung, change to gpt-3.5
        messages=[
            {"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # print(prompt)
    return response.choices[0].message.content

num_chunks_to_process = 1
total_chunks_processed = 0

# Process data in chunks
responses = pd.DataFrame(columns=['conv_id', 'Test2.1_response'])

for chunk_number, chunk in enumerate(thesis_df_reader):
    if chunk_number >= num_chunks_to_process:
        break
    chunk_responses = process_chunk(chunk)
    total_chunks_processed += 1
    responses = pd.concat([responses, chunk_responses], ignore_index=True)

# Save the dataframe to a CSV file
responses.to_csv("test21_responses_chunked.csv", index=False)


###OLD CODE:
'''import pandas as pd
import numpy as np
import openai

# Set pandas display options to show all rows and columns
pd.set_option('display.max_colwidth', None)

# Data Processing:
data_path = "/Users/ivannagodoymunoz/Desktop/Master Thesis/Testing"
data_chunksize = 18  # Define the chunk size

openai.api_key = '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'

emotion_labels = ["surprised", "excited", "angry", "proud", "sad", "annoyed",
                  "grateful", "lonely", "afraid", "terrified", "guilty", "impressed",
                  "disgusted", "hopeful", "confident", "furious", "anxious", "anticipating",
                  "joyful", "nostalgic", "disappointed", "prepared", "jealous", "content",
                  "devastated", "sentimental", "embarrassed", "caring", "trusting", "ashamed",
                  "apprehensive", "faithful"]

# Function to process chunks ensuring conversations are not divided
def process_chunks(num_chunks_to_process):
    responses = pd.DataFrame(columns=['conv_id', 'Test2.1_response'])
    thesis_df_reader = pd.read_csv(f"{data_path}/thesis_data.csv", sep=",", chunksize=data_chunksize)
    chunks_processed = 0

    while chunks_processed < num_chunks_to_process:
        conversation = pd.DataFrame()
        for chunk_number, chunk in enumerate(thesis_df_reader):
            if 'conv_id' not in chunk.columns:
                raise ValueError("The 'conv_id' column is required for conversation grouping.")

            if len(conversation) == 0:
                conversation = chunk
            else:
                conversation = pd.concat([conversation, chunk])

            unique_conversations = conversation['conv_id'].nunique()
            if unique_conversations <= 0:
                continue

            if len(conversation) >= data_chunksize or unique_conversations > 1:
                responses = pd.concat([responses, process_chunk(conversation)], ignore_index=True)
                conversation = pd.DataFrame()
                chunks_processed += 1
                if chunks_processed >= num_chunks_to_process:
                    break
        # Reset the iterator to read from the beginning of the file
        thesis_df_reader = pd.read_csv(f"{data_path}/thesis_data.csv", sep=",", chunksize=data_chunksize)

    return responses


def process_chunk(chunky):
    conv_sample = chunky.groupby('conv_id')['utterance'].apply(list).reset_index().sort_values(by='conv_id')
    # Extract unique conversation IDs from grouped_data
    conversation_ids = conv_sample['conv_id'].tolist()
    # Extract emotion labels corresponding to the conversation IDs
    emotions_list = chunky.groupby('conv_id')['emotion_label'].unique().tolist()
    emotions_list = np.concatenate(emotions_list).tolist()
    # Create a new dataframe to store the listener responses
    responses_chunk = pd.DataFrame(columns=['conv_id', 'Test2.1_response'])

    for index, row in conv_sample.iterrows():
        conv_id = row['conv_id']
        conversation_context = chunky.loc[chunky['conv_id'] == conv_id, 'context'].iloc[0]
        # Extract emotion labels for the conversation
        emotions = chunky.loc[chunky['conv_id'] == conv_id, 'emotion_label'].tolist()
        # Selecting the most frequent emotion label for the conversation
        emotion = max(set(emotions), key=emotions.count)
        # Extract first utterance for the empathetic response
        first_utterance = row['utterance'][0]
        # Generate empathetic response
        empathetic_response = generate_empathetic_response(conversation_context, emotion, first_utterance)
        # Save the conversation ID and listener response in the dataframe
        new_row = pd.DataFrame({
            'conv_id': [conv_id],
            'Test2.1_response': [empathetic_response]
        })
        responses_chunk = pd.concat([responses_chunk, new_row], ignore_index=True)
    return responses_chunk


# Function to generate empathetic responses based on situation, emotion, and the first utterance
def generate_empathetic_response(context, emotion, first_utterance):
    prompt = f"Consider a situation and the emotion of a speaker. Situation: {context}\nEmotion: {emotion}\nAct as the listener and reply to the speaker.\nSpeaker: {first_utterance}\nListener:"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",  #Achtung, change to gpt-3.5
        messages=[
            {"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # print(prompt)
    return response.choices[0].message.content


num_chunks_to_process = 3

# Process data in chunks
responses = process_chunks(num_chunks_to_process)

# Save the dataframe to a CSV file
responses.to_csv("test21_responses_chunked.csv", index=False)'''