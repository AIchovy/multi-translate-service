import struct
import logging
from typing import List, Tuple, Dict
from collections import defaultdict

def generate_binary_file(
    texts: List[Tuple[str, str, str, str]],
    output_file: str = "stories.bin"
) -> None:
    """
    Generate a binary file containing multi-language text data.
    """

    try:
        # 1. sort texts by language and text_id
        texts = sorted(texts, key=lambda x: (x[0], x[1]))
        num_records = len(texts)
        logging.info(f"Total {num_records} records")

        # 2. initialize index and data area
        index_records = []
        data_content = bytearray()
        current_offset = 0

        # 3. build data and index records
        for language, text_id, source, content in texts:
            # validate input
            if len(language.encode('utf-8')) > 8:
                logging.error(f"language code {language} is too long")
                raise ValueError(f"language code {language} is too long")
            if len(text_id.encode('utf-8')) > 16:
                logging.error(f"text id {text_id} is too long")
                raise ValueError(f"text id {text_id} is too long")
            if len(source.encode('utf-8')) > 5:
                logging.error(f"source {source} is too long")
                raise ValueError(f"source {source} is too long")
            if source not in ["TEXT", "AUDIO"]:
                logging.error(f"invalid source {source}")
                raise ValueError(f"source {source} must be TEXT or AUDIO")

            # encode text content to UTF-8
            content_bytes = content.encode('utf-8')
            content_length = len(content_bytes)

            # add to data area
            data_content.extend(content_bytes)

            # create index record
            index_records.append({
                'language': language,
                'text_id': text_id,
                'source': source,
                'offset': current_offset,
                'length': content_length
            })

            # update offset
            current_offset += content_length

        # 4. calculate metadata
        index_record_size = 41  
        index_length = num_records * index_record_size
        data_offset = 16 + index_length 

        # 5. write to binary file
        with open(output_file, 'wb') as f:
            # write metadata header
            f.write(struct.pack('<IIQ', num_records, index_length, data_offset))
            logging.info(f"metadata header: num_records={num_records}, index_length={index_length}, data_offset={data_offset}")

            # write index area
            for record in index_records:
                f.write(record['language'].encode('utf-8').ljust(8, b'\x00'))  # language code, left padding
                f.write(record['text_id'].encode('utf-8').ljust(16, b'\x00'))  # text id, left padding
                f.write(record['source'].encode('utf-8').ljust(5, b'\x00'))   # source, left padding
                f.write(struct.pack('<QI', record['offset'], record['length'])) # offset and length
            logging.info(f"index area written, total {num_records} records")

            # write data area
            f.write(data_content)
            logging.info(f"data area written, total {len(data_content)} bytes")

        logging.info(f"binary file {output_file} generated successfully")

    except Exception as e:
        logging.error(f"failed to generate binary file: {str(e)}")
        raise

if __name__ == "__main__":
    
    sample_texts = [
        ("en", "0", "TEXT", "Hello, world!"),
        ("en", "1", "AUDIO", "This is a test."),
        ("zh-Hans", "2", "TEXT", "你好，世界！"),
        ("zh-Hans", "3", "AUDIO", "这是一个测试。"),
        ("zh-Hant", "4", "TEXT", "妳好，世界！"),
        ("zh-Hant", "5", "AUDIO", "這是一個測試。"),
        ("ja", "6", "TEXT", "こんにちは、世界！"),
        ("ja", "7", "AUDIO", "これはテストです。"),
    ]

    try:
        generate_binary_file(sample_texts, "stories.bin")
    except Exception as e:
        logging.error(f"script failed: {str(e)}")