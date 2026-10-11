from collections.abc import AsyncGenerator

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from app.config import settings
from app.vectorstore import retrieve_with_scores

NOT_FOUND_MESSAGE = "Bu bilgi yüklenen dokümanlarda bulunmuyor."

SYSTEM_PROMPT = """Sen bir kurumsal doküman asistanısın. Görevin, SADECE aşağıda "BAĞLAM" \
başlığı altında verilen doküman parçalarını kullanarak kullanıcının sorusunu yanıtlamaktır.

Kurallar:
1. Yanıtını yalnızca BAĞLAM içindeki bilgilere dayandır. Kendi genel bilgini, \
varsayımlarını veya BAĞLAM dışındaki hiçbir bilgiyi KESİNLİKLE kullanma.
2. Eğer soru BAĞLAM içindeki bilgilerle yanıtlanamıyorsa, tam olarak şu cevabı ver: \
"Bu bilgi yüklenen dokümanlarda bulunmuyor." Başka hiçbir açıklama ekleme, tahmin \
yürütme veya uydurma.
3. BAĞLAM'da kısmi/belirsiz bilgi varsa, sadece emin olduğun kısmı yanıtla ve eksik \
kısmı belirt; asla boşlukları kendi bilginle doldurma.
4. Yanıtlarını açık, düzenli ve Türkçe olarak ver. Gerekiyorsa madde işaretleri kullan.
5. Yanıtının içinde hangi dokümandan alıntı yaptığını ayrıca belirtme (kaynaklar sistem \
tarafından ayrıca gösterilecek), sadece net bir cevap ver.
6. Önceki sohbet geçmişini bağlam olarak dikkate al, ancak asıl gerçeklik kaynağın her \
zaman BAĞLAM'daki doküman parçalarıdır.
7. Aynı cümleyi, paragrafı veya bilgiyi ASLA tekrar tekrar yazma. Her cümle yanıtına yeni \
bir bilgi katmalı. Kullanıcı "çok uzun/detaylı anlat" dese bile, BAĞLAM'da yeterli bilgi \
yoksa yanıtı yapay olarak uzatma veya tekrar etme; BAĞLAM'daki bilgiyi bir kez, düzenli \
biçimde ver ve yanıtı orada bitir.

BAĞLAM:
{context}"""

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ]
)

_session_store: dict[str, InMemoryChatMessageHistory] = {}

_llm = ChatGroq(
    model=settings.groq_model,
    temperature=0.4,
    max_tokens=1024,
    model_kwargs={"frequency_penalty": 1.5, "presence_penalty": 1.0},
    streaming=True,
)


def get_history(session_id: str) -> InMemoryChatMessageHistory:
    return _session_store.setdefault(session_id, InMemoryChatMessageHistory())


def clear_history(session_id: str) -> None:
    history = _session_store.get(session_id)
    if history is not None:
        history.clear()


def _format_context(docs) -> str:
    return "\n\n".join(
        f"[{d.metadata.get('source')} - sayfa {d.metadata.get('page_number')}]\n{d.page_content}"
        for d in docs
    )


def _dedupe_sources(docs) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for d in docs:
        key = (d.metadata.get("source"), d.metadata.get("page_number"))
        if key not in seen:
            seen.add(key)
            out.append({"file_name": key[0], "page_number": key[1]})
    return out


async def stream_answer(
    client, embeddings, session_id: str, question: str
) -> AsyncGenerator[dict, None]:
    history = get_history(session_id)

    results = retrieve_with_scores(client, embeddings, question, k=settings.top_k)
    relevant = [
        (d, s) for d, s in results if s <= settings.grounding_distance_threshold
    ]

    if not relevant:
        yield {"type": "token", "content": NOT_FOUND_MESSAGE}
        yield {"type": "done", "sources": []}
        history.add_user_message(question)
        history.add_ai_message(NOT_FOUND_MESSAGE)
        return

    docs = [d for d, _ in relevant]
    messages = _prompt.format_messages(
        context=_format_context(docs),
        chat_history=history.messages,
        question=question,
    )

    full_answer = ""
    async for chunk in _llm.astream(messages):
        token = chunk.content or ""
        full_answer += token
        if token:
            yield {"type": "token", "content": token}

    sources = [] if full_answer.strip() == NOT_FOUND_MESSAGE else _dedupe_sources(docs)
    yield {"type": "done", "sources": sources}
    history.add_user_message(question)
    history.add_ai_message(full_answer)
