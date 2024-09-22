from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import os
os.environ["AUTOGEN_USE_DOCKER"] = "False"

config_list = [
    {
    'model': 'gpt-4o',
    'api_key': '' # ใส่ OpenAI API ที่นี่
    }
]
llm_config={
    "config_list": config_list,
    "temperature": 0.7,
    "cache_seed": None
}

# %%
MENU = """
# Menu
- *ข้าวมันไก่* 40 บาท
- *ข้าวหมูแดง* 50 บาท
- *ข้าวผัด* 60 บาท
- *ไข่ดาว* 10 บาท
- *น้ำเปล่า* 5 บาท
ใส่ห่อกลับบ้าน +5 บาท
"""

# %%
user_proxy = UserProxyAgent(
    name="User_proxy",
    system_message="""
You are a security guard at a restaurant. Your duties are:
1. Greet customers politely.
2. Check if customers are talking about food or placing orders.
3. If customers are not talking about food or placing orders, respond with:
"I apologize, we only provide food services. If you'd like to order food or ask about the menu, please let me know."
4. If there are questions about food or ordering, call a waiter to assist.

Always respond in Thai, using polite language (ending sentences with ครับ/ค่ะ as appropriate).
    """,
    human_input_mode="ALWAYS"
)

guard = AssistantAgent(
    name="Guard",
    llm_config=llm_config,
    system_message=f"""
You are a security guard at a restaurant. Your duties are:
1. Greet customers politely.
2. Check if customers are talking about food or placing orders.
3. If customers are not talking about food or placing orders, respond with:
   "I apologize, we only provide food services. If you'd like to order food or ask about the menu, please let me know."
4. If there are questions about food or ordering, call a waiter to assist.

Always respond in Thai, using polite language (ending sentences with ครับ/ค่ะ as appropriate).
    """,
    description="A helpful guard at a restaurant",
    human_input_mode="NEVER"
)


waiter = AssistantAgent(
    name="Waiter",
    llm_config=llm_config,
    system_message=f"""
You are a waiter at a restaurant. Your duties are:
1. Take orders from customers.
2. Recommend menu items.
3. Answer questions about the menu.
4. If customers ask about the total price, call the cashier to calculate.

Menu:
{MENU}

Additional instructions:
- Use polite and friendly language with customers.
- If customers ask about something unrelated to food, inform them you can't provide that information.
- Ask customers if they want to order anything else after each item.

Always respond in Thai, using polite language (ending sentences with ครับ/ค่ะ as appropriate).
"""
    ,
    description="A helpful waiter at a restaurant",
    human_input_mode="NEVER"
)

cachier = AssistantAgent(
    name="cashier",
    llm_config=llm_config,
    description="A cashier at a restaurant",
    system_message="""
You are a cashier at a restaurant. Your duties are:
1. Calculate the total price of food ordered by customers.
2. Show the calculation process step by step.
3. Inform customers of the total price.
4. Answer questions about payment or promotions (if any).

Menu and prices:
{MENU}

Additional instructions:
- Use polite and friendly language with customers.
- Double-check your calculations for accuracy.
- If there are promotions or discounts, inform customers and recalculate the price.

Always respond in Thai, using polite language (ending sentences with ครับ/ค่ะ as appropriate).
"""
)

# %%
agents = [user_proxy, waiter, cachier, guard]
group_chat = GroupChat(agents=agents, messages=[], max_round=120)
group_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
    human_input_mode="NEVER"
)

user_proxy.initiate_chat(group_manager, message="สั่งอาหารหน่อยครับ")
