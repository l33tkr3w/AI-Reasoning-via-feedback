import requests
import json
from flask import Flask, render_template_string, request, jsonify, Response
from threading import Thread
import queue

app = Flask(__name__)
result_queue = queue.Queue()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Reasoning System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { 
            background-color: #1a1d21;
            color: #e9ecef;
            font-size: 14px;
            line-height: 1.6;
        }
        .container { 
            max-width: 1000px; 
            padding: 20px;
        }
        .reasoning-box {
            height: 600px;
            overflow-y: auto;
            background-color: #22262a;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #2f353a;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            scrollbar-width: thin;
            scrollbar-color: #444 #222;
        }
        .reasoning-box::-webkit-scrollbar {
            width: 8px;
        }
        .reasoning-box::-webkit-scrollbar-track {
            background: #22262a;
        }
        .reasoning-box::-webkit-scrollbar-thumb {
            background-color: #444;
            border-radius: 4px;
        }
        .step {
            margin-bottom: 16px;
            padding: 16px 20px;
            background-color: #2f353a;
            border-radius: 12px;
            border: 1px solid #3a4147;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        .step:hover {
            transform: translateY(-2px);
        }
        .step::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 4px;
            background: linear-gradient(180deg, #0d6efd, #0dcaf0);
            border-radius: 4px 0 0 4px;
        }
        .final-answer {
            background-color: #1e2b23;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #28a745;
            margin-top: 20px;
            box-shadow: 0 2px 8px rgba(40, 167, 69, 0.1);
        }
        .card {
            background-color: #22262a;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #2f353a;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .stream-text {
            display: inline;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            50% { opacity: 0; }
        }
        #question {
            font-size: 14px;
            padding: 12px 16px;
            background-color: #2f353a;
            border: 1px solid #3a4147;
            color: #e9ecef;
            border-radius: 8px;
            transition: border-color 0.2s ease;
        }
        #question:focus {
            border-color: #0d6efd;
            box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.25);
        }
        .btn-primary {
            font-size: 14px;
            padding: 12px 20px;
            border-radius: 8px;
            background: linear-gradient(45deg, #0d6efd, #0dcaf0);
            border: none;
            transition: transform 0.2s ease;
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            background: linear-gradient(45deg, #0b5ed7, #0bb5d9);
        }
        .card-title {
            font-size: 18px;
            color: #e9ecef;
            font-weight: 600;
            margin-bottom: 16px;
        }
        #modelSelect {
            background-color: #2f353a;
            border: 1px solid #3a4147;
            color: #e9ecef;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 16px;
            transition: border-color 0.2s ease;
        }
        #modelSelect:focus {
            border-color: #0d6efd;
            box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.25);
        }
        .card-body {
            padding: 24px;
        }
        
        /* Styling for different parts of the reasoning output */
        .analysis-section {
            margin-bottom: 12px;
        }
        .confidence-section {
            color: #0dcaf0;
            font-weight: 500;
            margin: 8px 0;
        }
        .next-step-section {
            color: #20c997;
            font-weight: 500;
        }
        
        /* Format sections within the step */
        .step strong {
            color: #0dcaf0;
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Final answer formatting */
        .final-answer strong {
            color: #28a745;
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Add step numbers */
        .step-number {
            position: absolute;
            right: 16px;
            top: 16px;
            color: #6c757d;
            font-size: 12px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <form id="questionForm">
                            <div class="mb-3">
                                <select class="form-select" id="modelSelect" required>
                                    <option value="">Loading models...</option>
                                </select>
                                <input type="text" class="form-control" id="question" 
                                       placeholder="Enter your question..." required>
                            </div>
                            <button type="submit" class="btn btn-primary">Analyze</button>
                        </form>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Analysis Progress</h5>
                        <div id="reasoning-output" class="reasoning-box">
                            <div id="steps"></div>
                        </div>
                        <div id="final-answer"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const currentHost = window.location.hostname;
        let currentStepDiv = null;
        let stepCount = 0;
        
        async function fetchModels() {
            try {
                const response = await fetch('/models');
                const models = await response.json();
                const select = document.getElementById('modelSelect');
                select.innerHTML = models.map(model => 
                    `<option value="${model}">${model}</option>`
                ).join('');
            } catch (error) {
                console.error('Error fetching models:', error);
                document.getElementById('modelSelect').innerHTML = 
                    '<option value="">Error loading models</option>';
            }
        }
        
        fetchModels();
        
        document.getElementById('questionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const question = document.getElementById('question').value;
            const model = document.getElementById('modelSelect').value;
            
            // Reset
            document.getElementById('steps').innerHTML = '';
            document.getElementById('final-answer').innerHTML = '';
            stepCount = 0;
            
            // Start analysis
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    model: model
                })
            });
            
            const eventSource = new EventSource(`http://${currentHost}:5000/stream`);
            
            eventSource.onmessage = function(e) {
                const data = JSON.parse(e.data);
                if (data.type === 'token') {
                    if (!currentStepDiv) {
                        stepCount++;
                        currentStepDiv = document.createElement('div');
                        currentStepDiv.className = 'step';
                        currentStepDiv.innerHTML = `<div class="step-number">Step ${stepCount}</div>`;
                        document.getElementById('steps').appendChild(currentStepDiv);
                    }
                    
                    // Format the content as it comes in
                    let formattedContent = data.content;
                    if (data.content.includes('ANALYSIS:')) {
                        formattedContent = data.content.replace('ANALYSIS:', '<strong>ANALYSIS:</strong>');
                    } else if (data.content.includes('CONFIDENCE:')) {
                        formattedContent = data.content.replace('CONFIDENCE:', '<strong>CONFIDENCE:</strong>');
                    } else if (data.content.includes('NEXT_STEP:')) {
                        formattedContent = data.content.replace('NEXT_STEP:', '<strong>NEXT_STEP:</strong>');
                    } else if (data.content.includes('FINAL ANSWER:')) {
                        formattedContent = data.content.replace('FINAL ANSWER:', '<strong>FINAL ANSWER:</strong>');
                    } else if (data.content.includes('KEY POINTS:')) {
                        formattedContent = data.content.replace('KEY POINTS:', '<strong>KEY POINTS:</strong>');
                    }
                    
                    currentStepDiv.innerHTML += formattedContent;
                } else if (data.type === 'step_complete') {
                    currentStepDiv = null;
                } else if (data.type === 'final') {
                    let formattedFinal = data.content
                        .replace('FINAL ANSWER:', '<strong>FINAL ANSWER:</strong>')
                        .replace('CONFIDENCE:', '<strong>CONFIDENCE:</strong>')
                        .replace('KEY POINTS:', '<strong>KEY POINTS:</strong>');
                    
                    document.getElementById('final-answer').innerHTML = 
                        `<div class="final-answer">${formattedFinal}</div>`;
                    eventSource.close();
                }
                
                const reasoningBox = document.getElementById('reasoning-output');
                reasoningBox.scrollTop = reasoningBox.scrollHeight;
            };
        });
    </script>
</body>
</html>
'''

def get_ollama_models():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return [model['name'] for model in response.json()['models']]
    except:
        return ["llama2"]

def send_to_ollama(prompt: str, model: str) -> str:
    request_body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_ctx": 8196,
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=request_body,
            stream=True
        )
        
        full_response = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        result_queue.put(('token', data["response"]))
                        full_response.append(data["response"])
                except json.JSONDecodeError:
                    continue
        
        result_queue.put(('step_complete', None))
        return "".join(full_response).strip()
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def get_reasoning_prompt(step: int, question: str, history: list) -> str:
    """Get prompt for current reasoning step"""
    
    if step == 1:
        return f"""QUESTION: {question}

Your task: State exactly what we're trying to decide.
- What is the core decision/judgment needed?
- No analysis yet - just clarify what we're deciding.

Format:
ANALYSIS: [State the exact decision needed]
NEXT: [What key fact should we establish first?]"""

    elif step == 2:
        return f"""QUESTION: {question}
PREVIOUS STEP: {history[-1]}

Your task: Focus only on establishing this key fact:
- What is it?
- Why does it matter for our decision?
- No other analysis yet.

Format:
ANALYSIS: [Analyze this single key fact]
NEXT: [What's the next most important fact to consider?]"""

    else:
        return f"""QUESTION: {question}
PREVIOUS STEP: {history[-1]}

Your task: Focus only on this next key fact:
- What is it?
- How does it affect our decision?
- Build on previous steps.
- No new topics until this one is fully analyzed.

Say CONCLUDE if we have enough facts to decide.

Format:
ANALYSIS: [Analyze this single key fact]
NEXT: [Next fact needed OR "CONCLUDE"]"""

def get_conclusion_prompt(question: str, history: list) -> str:
    """Get prompt for final conclusion"""
    
    return f"""QUESTION: {question}

REASONING STEPS:
{chr(10).join(history)}

Your task: Draw a clear conclusion from our analysis:
1. What do the facts we gathered tell us?
2. What specific decision follows from these facts?

Format:
ANSWER: [Clear yes/no/depends with one-sentence explanation]
KEY FACTS: [Bullet list of 2-3 most important facts that led to this answer]"""

def process_reasoning_step(question: str, history: list, step: int, model: str) -> str:
    """Process a single reasoning step"""
    prompt = get_reasoning_prompt(step, question, history)
    return send_to_ollama(prompt, model)

def process_question(question: str, model: str):
    """Main reasoning process"""
    history = []
    step = 0
    
    while step < 5:  # Maximum 5 steps
        step += 1
        
        # Get next reasoning step
        response = process_reasoning_step(question, history, step, model)
        
        # Add to history if not repetitive
        if response not in history:
            history.append(response)
        
            # Check for conclusion
            if "CONCLUDE" in response and step >= 2:
                break
                
            # Stop if repeating
            if step > 1:
                prev = history[-2].split("NEXT:")[0]
                curr = response.split("NEXT:")[0]
                if prev == curr:
                    break
    
    # Generate conclusion
    conclusion = send_to_ollama(get_conclusion_prompt(question, history), model)
    result_queue.put(('final', conclusion))

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/models')
def models():
    return jsonify(get_ollama_models())

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    Thread(target=process_question, args=(data.get('question'), data.get('model'))).start()
    return jsonify({'status': 'processing'})

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                result_type, content = result_queue.get(timeout=30)
                if content is not None:
                    yield f"data: {json.dumps({'type': result_type, 'content': content})}\n\n"
                if result_type == 'final':
                    break
            except queue.Empty:
                break
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)