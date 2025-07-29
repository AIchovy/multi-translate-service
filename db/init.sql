-- Create extension for UUID generation if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create translation_tasks table
CREATE TABLE translation_tasks (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Task identification
    task_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Input data
    audio_url TEXT NOT NULL,
    original_text TEXT,
    target_languages JSONB NOT NULL,
    
    -- Task status and tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Processing results
    stt_result JSONB,
    translation_results JSONB,
    
    -- Error handling
    error_message TEXT
);

-- Create indexes for better query performance
CREATE INDEX idx_translation_tasks_id ON translation_tasks(id);
CREATE INDEX idx_translation_tasks_task_id ON translation_tasks(task_id);
CREATE INDEX idx_translation_tasks_status ON translation_tasks(status);

-- Create trigger for automatic updated_at timestamp update
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_translation_tasks_updated_at
    BEFORE UPDATE ON translation_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE translation_tasks IS 'Translation task model for Multi Translate Service';
COMMENT ON COLUMN translation_tasks.id IS 'Primary key UUID';
COMMENT ON COLUMN translation_tasks.task_id IS 'Unique task identifier';
COMMENT ON COLUMN translation_tasks.audio_url IS 'URL of the audio file to be processed';
COMMENT ON COLUMN translation_tasks.original_text IS 'Original text from speech-to-text';
COMMENT ON COLUMN translation_tasks.target_languages IS 'Array of target language codes';
COMMENT ON COLUMN translation_tasks.status IS 'Task processing status';
COMMENT ON COLUMN translation_tasks.created_at IS 'Task creation timestamp';
COMMENT ON COLUMN translation_tasks.updated_at IS 'Last update timestamp';
COMMENT ON COLUMN translation_tasks.stt_result IS 'Speech-to-text result with metadata';
COMMENT ON COLUMN translation_tasks.translation_results IS 'Translation results for each target language';
COMMENT ON COLUMN translation_tasks.error_message IS 'Error message if task failed';