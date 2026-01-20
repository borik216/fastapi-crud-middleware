import asyncio
import httpx
import time

async def send_request(client, url, token):
    headers = {"access_token": token}
    start = time.perf_counter()
    try:
        response = await client.get(url, headers=headers)
        latency = time.perf_counter() - start
        return response.status_code, latency
    except Exception as e:
        return "Error", 0

async def main():
    url = "http://localhost:8000/inspect-traffic"
    token = "cp-secure-key-2026"
    num_requests = 100
    
    print(f"--- Starting Stress Test: {num_requests} requests ---")
    
    async with httpx.AsyncClient() as client:
        tasks = [send_request(client, url, token) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    # Calculate Results
    latencies = [r[1] for r in results if r[0] == 200]
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print(f"Successes: {len(latencies)}/{num_requests}")
        print(f"Average Latency: {avg_latency:.4f}s")
        print(f"Max Latency: {max(latencies):.4f}s")
    else:
        print("All requests failed. Is your Docker container running?")

if __name__ == "__main__":
    asyncio.run(main())