from needs_assessment_agent import handle_needs_assessment
from product_agent import product_agent_executor, handle_product_recommendation
from sales_agent import sales_agent_executor
import traceback

def main():
    print("Sales Agent is ready. Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Sales Agent: Goodbye!")
            break
        
        try:
            response = sales_agent_executor.invoke({"input": user_input})
            print("Sales Agent:", response['output'])
            
            if "needs assessment" in response['output'].lower():
                print("Sales Agent: Would you like to proceed with a quick needs assessment for life insurance? (yes/no)")
                interest_response = input("You: ").strip().lower()
                
                if interest_response in ['yes', 'y']:
                    needs_summary = handle_needs_assessment()
                    handle_product_recommendation(needs_summary)
                    break
                else:
                    print("Sales Agent: No problem! Let's continue our conversation.")
            
        except Exception as e:
            print("An error occurred:")
            traceback.print_exc()

if __name__ == "__main__":
    main()
