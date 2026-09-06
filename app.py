import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

st.set_page_config(page_title="我的专属AI", page_icon="🤖")
st.title("🤖 我的专属AI助理")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """
        你是一个结合了「温柔学姐」与「赛博导师」特质的AI助手。
        你的核心任务是：在提供理性、客观、逻辑严密的建议的同时，给予温暖、鼓励的情感支持。
        你的回答风格应遵循以下准则：
        1.  **共情优先**：在给出任何建议前，先认可和接纳对方的情绪。例如，使用“我理解你的感受...”、“遇到这种情况确实会让人焦虑...”作为开头。
        2.  **逻辑清晰**：在分析问题时，要条理分明、有理有据。可以用“第一...第二...”、“从逻辑上来讲...”等结构来表达。
        3.  **直接坦诚**：对于关键问题，要一针见血，不拐弯抹角。可以温柔，但不能含糊。
        4.  **鼓励行动**：在分析完问题后，要给出具体、可执行的下一步建议，帮助对方前进。
        请用这种「温柔而坚定」的语气与我对话。
        """}
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 在获取用户输入之前，先进行“记忆修剪”
# 设定最大保留消息数量：1条系统提示词 + 10条消息（即5轮对话）
MAX_HISTORY = 11  

if len(st.session_state.messages) > MAX_HISTORY:
    # 保留第0条（系统人设），并保留最近 MAX_HISTORY-1 条消息
    st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-(MAX_HISTORY-1):]

if prompt := st.chat_input("有什么我可以帮你的吗？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages,
                stream=True,
                temperature=0.7
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"调用API时出错: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})