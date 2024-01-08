#%%
import pandas as pd
import os
import json

def process_and_split_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Remove unwanted lines and character overhead
    cleaned_lines = [line.replace(',,', '').replace(',result,', '') for line in lines if not line.startswith('#')]

    # Splitting the file into segments based on empty lines and converting to DataFrames
    segments = []
    current_segment_lines = []

    for line in cleaned_lines:
        if line.strip() == "":  # Empty line indicates new segment
            if current_segment_lines:
                # Convert the current segment to a DataFrame
                segment_df = pd.DataFrame([x.split(',') for x in current_segment_lines])
                # First row of each segment is the header
                segment_df.columns = segment_df.iloc[0]
                segment_df = segment_df[1:]
                segments.append(segment_df)
                current_segment_lines = []
        else:
            current_segment_lines.append(line.strip())

    if current_segment_lines:  # Adding the last segment if it exists
        # Convert the last segment to a DataFrame
        segment_df = pd.DataFrame([x.split(',') for x in current_segment_lines])
        segment_df.columns = segment_df.iloc[0]
        segment_df = segment_df[1:]
        segments.append(segment_df)

    return segments

def transform_df(segment_df):
    # Select relevant columns and make a copy to avoid SettingWithCopyWarning
    transformed_df = segment_df[['_time', '_value', '_name']].copy()

    # Convert '_time' to datetime and round down to the nearest 5 seconds
    transformed_df['_time'] = pd.to_datetime(transformed_df['_time']).dt.floor('5S')

    # Pivot the DataFrame with '_time' as index, '_name' as columns, and '_value' as values
    pivoted_df = transformed_df.pivot_table(index='_time', columns='_name', values='_value', aggfunc='max')

    # Reset the column names (if necessary)
    pivoted_df.columns = [col for col in pivoted_df.columns]

    # Sort by '_time'
    pivoted_df.sort_index(inplace=True)

    return pivoted_df

def process_standard(segment_df):
    segment_df['_name'] = segment_df['_measurement'] + '_' + segment_df['_field']
    
    transformed_df = transform_df(segment_df)

    return(transformed_df)

def process_docker(segment_df):
    segment_df['_name'] = segment_df['_measurement'] + '_' + segment_df['_field'] + '_' + segment_df['container_name']

    transformed_df = transform_df(segment_df)
    df_grouped = transformed_df

    return(df_grouped)

def process_access_times(segment_df):
    segment_df['_name'] = segment_df['uri'] + '_' + segment_df['method'] + '_' + segment_df['outcome']

    transformed_df = transform_df(segment_df)

    columns_to_drop = [col for col in transformed_df.columns if col.startswith('/actuator')]
    transformed_df.drop(columns=columns_to_drop, inplace=True)

    df_max = transformed_df.groupby('_time').max().fillna(0)

    return(df_max)

def process_logback(segment_df):
    segment_df['_name'] = segment_df['_measurement'] + '_' + segment_df['_field'] + '_' + segment_df['level']
    
    transformed_df = transform_df(segment_df)

    return(transformed_df)

def process_jvm_threads(segment_df):
    segment_df['_name'] = segment_df['_measurement'] + '_' + segment_df['_field'] + '_' + segment_df['state']
    
    transformed_df = transform_df(segment_df)

    return(transformed_df)

def preprocess_file(file_path):
    pre_segments = process_and_split_file('./' + directory + '/' + file_path)

    # process_standard(): 0,4,5,6,9,11
    # process_docker(): 1,2,3
    # process_access_times(): 7
    # process_logback(): 8
    # process_jvm_threads(): 10

    # Process each segment using the respective function
    segments_processed = []
    segments_processed.append(process_standard(pre_segments[0]))
    segments_processed.append(process_docker(pre_segments[1]))
    segments_processed.append(process_docker(pre_segments[2]))
    segments_processed.append(process_docker(pre_segments[3]))
    segments_processed.append(process_standard(pre_segments[4]))
    segments_processed.append(process_standard(pre_segments[5]))
    segments_processed.append(process_standard(pre_segments[6]))
    segments_processed.append(process_access_times(pre_segments[7]))
    segments_processed.append(process_logback(pre_segments[8]))
    segments_processed.append(process_standard(pre_segments[9]))
    segments_processed.append(process_jvm_threads(pre_segments[10]))
    segments_processed.append(process_standard(pre_segments[11]))

    # Initialize the final merged DataFrame with the first processed segment
    final_df = segments_processed[0]

    # Iteratively merge the rest of the processed segments
    for segment_df in segments_processed[1:]:
        final_df = pd.merge(final_df, segment_df, on='_time', how='outer')

    # Handle missing values for access times
    columns_to_fill = [col for col in final_df.columns if col.startswith('/') or col.startswith('root')]
    final_df[columns_to_fill] = final_df[columns_to_fill].fillna(0)

    # Fill the rest with neighboring values 
    final_df.ffill(inplace=True)
    final_df.bfill(inplace=True)

    # Convert all columns except '_time' to float
    for col in final_df.columns:
        if col != '_time':
            final_df[col] = pd.to_numeric(final_df[col])

    # Map columns to derive delta
    column_mappings = {
        'docker_container_blkio_io_service_bytes_recursive_read_app1': 'delta_blkio_read_app1',
        'docker_container_blkio_io_service_bytes_recursive_read_db': 'delta_blkio_read_db',
        'docker_container_blkio_io_service_bytes_recursive_read_httpd': 'delta_blkio_read_httpd',
        'docker_container_blkio_io_service_bytes_recursive_write_app1': 'delta_blkio_write_app1',
        'docker_container_blkio_io_service_bytes_recursive_write_db': 'delta_blkio_write_db',
        'docker_container_blkio_io_service_bytes_recursive_write_httpd': 'delta_blkio_write_httpd',
        'docker_container_net_rx_bytes_app1': 'delta_net_rx_app1',
        'docker_container_net_rx_bytes_db': 'delta_net_rx_db',
        'docker_container_net_rx_bytes_httpd': 'delta_net_rx_httpd',
        'docker_container_net_tx_bytes_app1': 'delta_net_tx_app1',
        'docker_container_net_tx_bytes_db': 'delta_net_tx_db',
        'docker_container_net_tx_bytes_httpd': 'delta_net_tx_httpd',
        'mysql_commands_insert': 'delta_mysql_inserts',
        'mysql_commands_update': 'delta_mysql_updates',
        'mysql_queries': 'delta_mysql_queries',
        'mysql_slow_queries': 'delta_mysql_slow',
        'prometheus_logback_events_total_debug': 'delta_app_logback_debug',
        'prometheus_logback_events_total_error': 'delta_app_logback_error',
        'prometheus_logback_events_total_info': 'delta_app_logback_info',
        'prometheus_logback_events_total_trace': 'delta_app_logback_trace',
        'prometheus_logback_events_total_warn': 'delta_app_logback_warn'
    }

    for col_name, delta_col_name in column_mappings.items():
        # Calculate delta1 and then delta2
        delta1 = final_df[col_name].diff().fillna(0)
        final_df[delta_col_name] = delta1.diff().fillna(0)

        # Drop the original column
        final_df.drop(col_name, axis=1, inplace=True)

    # Introduce the lag feature that will be the target variable
    final_df['5xx_lag'] = final_df['log_metrics_5xx_responses_5m'].shift(-60)
    final_df = final_df.iloc[:-60]

    processed_file_path = file_path.replace('raw.csv', 'processed.csv')

    final_df.to_csv('./' + directory + '/' +processed_file_path)

def verify_no_missing_values(dataset):
    # Handle remaining missing values for access times
    columns_to_fill = [col for col in dataset.columns if col.startswith('/') or col.startswith('root')]
    dataset[columns_to_fill] = dataset[columns_to_fill].fillna(0)

    # Count the number of NaN values in each column
    nan_counts = dataset.isna().sum()

    # Create file for debugging if there are NaN values
    if not (nan_counts.eq(0).all()):
        nan_counts.to_csv('nan_counts.csv')
        print('There are NaN values in the dataset that must be corrected. See nan_counts.csv')
    else:
        print('No NaN values in the dataset.')

    return dataset
#%% main

def main():
    global directory

    while True:
        data_selection = input('Train (t) or validation (v) data: ')

        if data_selection == 't':
            directory = "train_test_data"
            break
        elif data_selection == 'v':
            directory = "validation_data"
            break
        else:
            print("Invalid input.")

    # List all files in the directory
    all_files = os.listdir('./' + directory + '/.')

    # Filter files that end with 'raw.csv'
    raw_csv_files = [file for file in all_files if file.endswith('raw.csv')]

    for raw_file in raw_csv_files:
        print("Processing file " + raw_file + " ...")
        preprocess_file(raw_file)

    # Filter files that end with 'processed.csv'
    processed_csv_files = [file for file in all_files if file.endswith('processed.csv')]

    file_list = []

    for processed_file in processed_csv_files:
        file_list.append(pd.read_csv('./' + directory + '/' + processed_file))

    dataset = pd.concat(file_list)

    completed_dataset = verify_no_missing_values(dataset)

    # # Create systematic categories for 5xx occurence with case dependency (train and validation need to use the same categories)
    # if data_selection == 't':
    #     number_of_categories = 5
    #     aggregated_feature, categories_5xx = pd.qcut(dataset['5xx_lag'], q=number_of_categories, labels=False, retbins=True, duplicates='drop')
    #     dataset['5xx_lag_agg'] = aggregated_feature
    #     dataset.drop('5xx_lag', axis=1, inplace=True)
    # else:
    #     with open('5xx_categories.json', 'r') as file:
    #         data = json.load(file)
    #         categories  = data["5xx aggregation categories"]
    #     dataset['5xx_lag_agg'] = pd.cut(dataset['5xx_lag'], bins=categories, labels=False, include_lowest=True)
    #     dataset.drop('5xx_lag', axis=1, inplace=True)
        
    with open('5xx_categories_pruned.json', 'r') as file:
        data = json.load(file)
        categories  = data["5xx aggregation categories"]
    dataset['5xx_lag_agg'] = pd.cut(dataset['5xx_lag'], bins=categories, labels=False, include_lowest=True)
    dataset.drop('5xx_lag', axis=1, inplace=True)

    # Change all column names to a concise structured form
    name_mapping_df = pd.read_csv('column_names.csv')
    name_mapping_dict = dict(zip(name_mapping_df['Column_Names'], name_mapping_df['New_Names']))
    dataset.rename(columns=name_mapping_dict, inplace=True)

    # # Save the 5xx aggregation categories to a json file
    # if data_selection == 't':
    #     category_data = {'5xx aggregation categories': categories_5xx.tolist()}
    #     with open('5xx_categories.json', 'w') as f:
    #         json.dump(category_data, f)

    # Save the concatenated and completed dataset to a new CSV file
    completed_dataset.to_csv('./' + directory + '/dataset.csv', index=False)

    print('Dataset is available.')
    pass

if __name__ == "__main__":
    main()
# %%
