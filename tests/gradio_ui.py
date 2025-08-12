import gradio as gr
from main import search_flights
# Define a simple chatbot response function
def chatbot_response(user_input, history=[]):
    best_flight_result = search_flights(str(user_input))
    # Append user input to the history
    history.append(("" + user_input, "" + f"{best_flight_result}"))
    return history, history

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 Flight Analyzer Assistant")

    chat_history = gr.Chatbot()
    user_input = gr.Textbox(label="Your Message", placeholder="Type your message here...")
    send_btn = gr.Button("Send")

    # Clear button to reset the chat
    clear_btn = gr.Button("Clear")

    # Define interactions
    send_btn.click(fn=chatbot_response, inputs=[user_input, chat_history], outputs=[chat_history, chat_history])
    clear_btn.click(fn=lambda: [], inputs=[], outputs=[chat_history])

# Launch the app
demo.launch()