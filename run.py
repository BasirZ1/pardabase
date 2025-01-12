from utils import add_new_admin_ps, generate_token

result = add_new_admin_ps(generate_token("basirzurmati"), "Basir Zurmati", "basirzurmati", "Basirzurmati", 5)
print(result)
