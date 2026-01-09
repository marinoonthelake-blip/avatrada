import os, json, uuid, re

class ChatManager:
    def __init__(self):
        self.path = "/home/avacado/avatrada/avatrada-brain/conversations"
        if not os.path.exists(self.path): 
            os.makedirs(self.path)

    def list_chats(self):
        chats = []
        for f in os.listdir(self.path):
            if f.endswith(".json"):
                full_p = os.path.join(self.path, f)
                try:
                    with open(full_p, 'r', encoding='utf-8') as j:
                        data = json.load(j)
                        title = data.get("title", "Saved Session")
                except:
                    title = "Salvaged Session"
                chats.append({"id": f.replace(".json", ""), "title": title, "ts": os.path.getmtime(full_p)})
        return sorted(chats, key=lambda x: x['ts'], reverse=True)

    def load_chat(self, chat_id):
        p = os.path.join(self.path, f"{chat_id}.json")
        try:
            with open(p, 'r', encoding='utf-8') as f: return json.load(f)
        except:
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()
                roles = re.findall(r'"role":\s*"(.*?)"', raw)
                conts = re.findall(r'"content":\s*\[\s*"(.*?)"', raw)
                return {"id": chat_id, "title": "Salvaged", "messages": [{"role": r, "content": [c]} for r, c in zip(roles, conts)]}

    def save_chat(self, chat_id, title, messages):
        clean = [{"role": m['role'], "content": [p for p in m['content'] if isinstance(p, str)]} for m in messages]
        with open(os.path.join(self.path, f"{chat_id}.json"), 'w', encoding='utf-8') as f:
            json.dump({"id": chat_id, "title": title, "messages": clean}, f, indent=2)

    def delete_chat(self, chat_id):
        p = os.path.join(self.path, f"{chat_id}.json")
        if os.path.exists(p): os.remove(p)

    def rename_chat(self, chat_id, new_title):
        data = self.load_chat(chat_id)
        if data:
            data["title"] = new_title
            self.save_chat(chat_id, new_title, data["messages"])

def get_chat_manager(): return ChatManager()
