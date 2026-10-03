from llm import LLM

def main():
    llm = LLM()
    
    response = llm.generate(
        "Explain Python loops for a beginner."
    )
    
    print(response)

if __name__ == "__main__":
    main()
