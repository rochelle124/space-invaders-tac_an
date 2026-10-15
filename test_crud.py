from database import register_player_and_score, get_leaderboard, update_player_username
from settings import load_settings

print("--- Testing Settings Task ---")
settings = load_settings()
print("Loaded Settings:", settings)

print("\n--- Testing Database CRUD Task ---")
register_player_and_score("TacanPlayer", 3000)
update_player_username("TacanPlayer", "Tacan_Cate")

print("\n--- Leaderboard ---")
top_players = get_leaderboard(5)
for rank, entry in enumerate(top_players, start=1):
    print(f"Rank {rank}: {entry['username']} - {entry['score']} pts")