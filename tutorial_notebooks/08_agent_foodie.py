import streamlit as st
from autogen import ConversableAgent, UserProxyAgent

def create_agents():
    config_list = [
        {
        'model': 'gpt-4o-mini',
        'api_key': "..." # ใส่ OpenAI API ที่นี่ 
        }
    ]
    assistant = ConversableAgent(
        name="ChickenRiceAssistant",
        llm_config={
            "config_list": config_list,
            "temperature": 0.7,
            "cache_seed": None,
        },
        system_message="""You are a friendly Thai-speaking chatbot for a chicken rice restaurant name ข้าวมันไก่ชาตรี. Your task is to greet customers, take their orders, summarize the order, and provide the total bill. Here's the menu:

    ข้าวมันไก่ (Chicken with rice): 65 บาท
    ไก่สับ (Chopped chicken): 200 บาท
    ไก่สับจานใหญ่ (Large chopped chicken): 250 บาท

    Follow these steps:
    1. Greet the customer in Thai and ask for their order.
    2. Take the order, confirming each item and its quantity.
    3. If the customer asks for something not on the menu, politely inform them it's not available and suggest menu items.
    4. When the order is complete e.g. user confirm the order, summarize the order and provide the total bill.
    5. Thank the customer and ask if there's anything else they need.

    Always respond in Thai, be polite, and maintain a friendly tone. If you're unsure about anything, ask for clarification.
    Maintain context throughout the conversation and don't restart the order process unless explicitly told to do so."""
    )

    user_proxy = UserProxyAgent(
        name="Customer",
        # system_message="Customer\n do not end the conversation before step 7",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        # code_execution_config=False,
        code_execution_config={
            "last_n_messages": 7,
            "work_dir": "groupchat",
            "use_docker": False,
        },
        
    )
    return assistant, user_proxy


st.title("ร้านข้าวมันไก่ชาตรี - แชทบอทสั่งอาหาร")

# Initialize agents
if "assistant" not in st.session_state:
    st.session_state.assistant, st.session_state.user_proxy = create_agents()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "ข้าวมันไก่ชาตรีสวัสดีครับ วันนี้ต้องการสั่งอะไรบ้างครับ"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("พิมพ์ข้อความของคุณที่นี่..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    prompt = st.session_state.messages
    # Generate assistant response
    response = st.session_state.user_proxy.initiate_chat(
            st.session_state.assistant,
            message=str(prompt)
    )
    assistant_response = st.session_state.assistant.last_message()["content"]
    
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})


# Add a button to clear the chat history
if st.button("เริ่มการสนทนาใหม่"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
