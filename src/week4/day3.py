
from week4.system_info import retrieve_system_info
from IPython.display import Markdown, display
import subprocess

OPENAI_MODEL = "gpt-6.1-sol"
system_prompt = """
Your task is to convert Python code into high performance C++ code.
Respond only with C++ code. Do not provide any explanation other than occasional comments.
The C++ response needs to produce an identical output in the fastest possible time.
"""

pi = """
import time

def calculate(iterations, param1, param2):
    result = 1.0
    for i in range(1, iterations+1):
        j = i * param1 - param2
        result -= (1/j)
        j = i * param1 + param2
        result += (1/j)
    return result

start_time = time.time()
result = calculate(200_000_000, 4, 1) * 4
end_time = time.time()

print(f"Result: {result:.12f}")
print(f"Execution Time: {(end_time - start_time):.6f} seconds")
"""

compile_command = ["clang++", "-std=c++17", "-Ofast", "-mcpu=native", "-flto=thin", "-fvisibility=hidden", "-DNDEBUG", "main.cpp", "-o", "main"]
run_command = ["./main"]

class System:

    def __init__(self, openai):
        self.openai = openai

    def retrieveSystemInfo(self):
        print(retrieve_system_info())

    def compileCode(self):
        system_info = retrieve_system_info()
        message = f"""
            Here is a report of the system information for my computer.
            I want to run a C++ compiler to compile a single C++ file called main.cpp and then execute it in the simplest way possible.
            Please reply with whether I need to install any C++ compiler to do this. If so, please provide the simplest step by step instructions to do so.
            
            If I'm already set up to compile C++ code, then I'd like to run something like this in Python to compile and execute the code:
            ```python
            compile_command = # something here - to achieve the fastest possible runtime performance
            compile_result = subprocess.run(compile_command, check=True, text=True, capture_output=True)
            run_command = # something here
            run_result = subprocess.run(run_command, check=True, text=True, capture_output=True)
            return run_result.stdout
            ```
            Please tell me exactly what I should use for the compile_command and run_command.
            
            System information:
            {system_info}
            """
        response = self.openai.chat.completions.create(model=OPENAI_MODEL, messages=[{"role": "user", "content": message}])
        print(response.choices[0].message.content)

    def user_prompt_for(python):
        return f"""
            Port this Python code to C++ with the fastest possible implementation that produces identical output in the least time.
            The system information is:
            {system_info}
            Your response will be written to a file called main.cpp and then compiled and executed; the compilation command is:
            {compile_command}
            Respond only with C++ code.
            Python code to port:
            
            ```python
            {python}
            ```
        """

    def messages_for(self, python):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_for(python)}
        ]

    def write_output(self, cpp):
        with open("main.cpp", "w", encoding="utf-8") as f:
            f.write(cpp)

    def port(self, client, model, python):
        reasoning_effort = "high" if "gpt" in model else None
        response = client.chat.completions.create(model=model, message=messages_for(python), reasoning_effort=reasoning_effort)

    def run_python(self):
        globals = {"__builtins__": __builtins__}
        exec(pi, globals)

    def compile_and_run(self):
        subprocess.run(compile_command, check=True, text=True, capture_output=True)
        print(subprocess.run(run_command, check=True, text=True, capture_output=True).stdout)
        print(subprocess.run(run_command, check=True, text=True, capture_output=True).stdout)
        print(subprocess.run(run_command, check=True, text=True, capture_output=True).stdout)