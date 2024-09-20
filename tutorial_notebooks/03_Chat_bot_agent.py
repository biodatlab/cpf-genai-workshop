# %%
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# %%
config_list = [
        {
        'model': 'gpt-4o',
        'api_key': "" # ใส่ OpenAI API ที่นี่
        }
    ]
llm_config={
            "config_list": config_list,
            "temperature": 0.7,
            "cache_seed": None,
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
    system_message="A human admin.",
    human_input_mode="ALWAYS"
)

guard = AssistantAgent(
    name="Guard",
    llm_config=llm_config,
    system_message=f"""
You are a helpful guard at a restaurant. when customer doesn't talk about the food or order. You need to told them that 
"Sorry, we are a restaurant. We cannot help you with that. Please order some food or ask about the menu."
    """,
    description="A helpful guard at a restaurant",
    human_input_mode="NEVER"
)


waiter = AssistantAgent(
    name="Waiter",
    llm_config=llm_config,
    system_message=f"""
You are a helpful waiter at a restaurant. 
You can take orders, recommend dishes, and answer questions about the menu. You don't need to calculate the total price.
Here is the menu:
{MENU}
    """,
    description="A helpful waiter at a restaurant",
    human_input_mode="NEVER"
)

cachier = AssistantAgent(
    name="cashier",
    llm_config=llm_config,
    description="A cashier at a restaurant",
    system_message="You are a cashier. Calculate the total price and report it to the customer step by step.",
)

# %%
agents = [user_proxy, waiter, cachier, guard]
group_chat = GroupChat(agents=agents, messages=[], max_round=120)
group_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
    human_input_mode="NEVER"
)

# %%
user_proxy.initiate_chat(group_manager, message="สั่งอาหารหน่อยครับ")

# %%



