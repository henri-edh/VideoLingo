import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from batch.utils.settings_check import check_settings
from batch.utils.video_processor import process_video
from batch.utils.config_updater import get_config_value, update_config
import pandas as pd
from rich.console import Console
from rich.panel import Panel
import time

console = Console()

def record_and_update_config(source_language, target_language):
    original_source_lang = get_config_value('SOURCE_LANGUAGE')
    original_target_lang = get_config_value('TARGET_LANGUAGE')
    
    if source_language:
        update_config('SOURCE_LANGUAGE', source_language)
    if target_language:
        update_config('TARGET_LANGUAGE', target_language)
    
    return original_source_lang, original_target_lang

def process_batch():
    if not check_settings():
        raise Exception("Settings check failed")

    df = pd.read_excel('batch/tasks_setting.xlsx')
    for index, row in df.iterrows():
        source_language = row['Source Language']
        target_language = row['Target Language']
        
        # Record current config and update if necessary
        original_source_lang, original_target_lang = record_and_update_config(source_language, target_language)
        
        try:
            status, error_step, error_message = process_video(row['Video File'], row['Dubbing'])
            status_msg = "Done" if status else f"Error: {error_step} - {error_message}"
        finally:
            # Restore original config
            update_config('SOURCE_LANGUAGE', original_source_lang)
            update_config('TARGET_LANGUAGE', original_target_lang)
        
        # update excel Status column
        df.at[index, 'Status'] = status_msg
        df.to_excel('batch/tasks_setting.xlsx', index=False)
        time.sleep(1)

    console.print(Panel("All tasks processed!\nCheck out in `batch/output`!", title="[bold green]Batch Processing Complete", expand=False))

if __name__ == "__main__":
    process_batch()