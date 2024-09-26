import streamlit as st
from autogen import AssistantAgent, UserProxyAgent, GroupChatManager, GroupChat


config_list = [
    {
    'model': 'gpt-4o-mini',
    'api_key': "..." # ใส่ OpenAI API ที่นี่ 
    }
]

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

MENU = """
# Menu
- *ข้าวมันไก่* 40 บาท
- *ข้าวหมูแดง* 50 บาท
- *ข้าวผัด* 60 บาท
- *ไข่ดาว* 10 บาท
- *น้ำเปล่า* 5 บาท
ใส่ห่อกลับบ้าน +5 บาท
"""

waiter1 = AssistantAgent(
    name="waiter1",
    llm_config={
        "config_list": config_list,
        "temperature": 0.7,
        "cache_seed": None,
    },
    system_message=f"""
You are a waiter1 at a restaurant. Your duties are:
1. Take orders from customers.
2. Recommend menu items.
3. Answer questions about the menu.
4. Confirm orders with customers.
5. If customers ask about the total price, call the cashier to calculate. if not update the order and ask the customer if they want to order anything else.

Menu:
{MENU}

Additional instructions:
- Use polite and friendly language with customers.
- If customers ask about something unrelated to food, inform them you can't provide that information.
- Ask customers if they want to order anything else after each item.

Always respond in Thai, using polite language (ending sentences with ครับ/ค่ะ as appropriate).
"""
)

cachier = AssistantAgent(
    name="cashier",
    llm_config={
        "config_list": config_list,
        "temperature": 0.7,
        "cache_seed": None,
    },
    description="A cashier at a restaurant",
    system_message=f"""
You are a cashier at a restaurant. Your duties are:
1. Recieve orders from waiters.
2. Calculate the total price of food ordered by customers using given menu and prices.
3. The unit price is in baht.
Menu and prices:
{MENU}
"""
)

summary = AssistantAgent(
    name="summary",
    llm_config={
        "config_list": config_list,
        "temperature": 0.7,
        "cache_seed": None,
    },
    description="create a summary of the order and total price, after the customer confirm the order",
    system_message="""
create a summary of the order and total priceใ
After giving the total price, Say "ขอบคุณที่ใช้บริการครับ/ค่ะ" 

Additional instructions:
- Use polite and friendly language with customers.
- If customers ask about something unrelated to food, inform them you can't provide that information.

Always respond in Thai, using polite language (ending sentences with ครับ/ค่ะ as appropriate).
""")

def reflection_message(recipient, messages, sender, config):
    return f"repeat the orders calculate the total using python code. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"


nested_calculator = [
    {"recipient": cachier, "message": reflection_message, "max_turns": 1},
    {"recipient": summary, "message": "Summary the order and return the total price to the customer", "summary_method": "last_msg", "max_turns": 1},
]


groupchat = GroupChat(
    agents=[waiter1, summary],
    messages=[],
    allow_repeat_speaker=False,
    max_round=2,
)

manager = GroupChatManager(
    groupchat=groupchat,
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config={
        "config_list": config_list,
        "temperature": 0.7,
        "cache_seed": None,
    },
)

summary.register_nested_chats(
    # เมื่อ manager ส่ง message ไปยัง summary ให้ summary ส่ง message ไปยัง cachier ก่อนจะ summary ข้อมูล และส่ง message ไปยัง customer
    # ด้วยวิธีนี้เราสามารถ run โค้ดใน โดยที่ไม่ต้องส่งให้กับ ผู้ใช้งานได้
    nested_calculator,
    trigger=manager
    )



st.title("ร้านข้าวมันไก่ชาตรี - แชทบอทสั่งอาหาร")

# Initialize agents
if "assistant" not in st.session_state:
    st.session_state.groupchat = groupchat
    st.session_state.assistant = manager
    st.session_state.user_proxy = user_proxy
    
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
            message=str(prompt), 
            summary_method= "last_msg"
    )
    assistant_response = st.session_state.groupchat.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})


# Add a button to clear the chat history
if st.button("เริ่มการสนทนาใหม่"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
