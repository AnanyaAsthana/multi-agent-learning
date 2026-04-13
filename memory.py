memory = []

def add_record(topic, score):
    memory.append({
        "topic": topic,
        "score": score
    })

def get_memory():
    return memory