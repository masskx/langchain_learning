import asyncio
import time

# 1. 函数前面加 async
async def make_changfen():
    print("🥟 开始做肠粉...")
    # 2. time.sleep 换成 await asyncio.sleep
    await asyncio.sleep(3)
    print("🥟 肠粉好了！")
    return "肠粉"

# TODO: 你来改 make_coffee 和 checkout
# async def make_coffee():
#     ...
# async def checkout():
#     ...

async def make_coffee():
    print("☕ 开始冲咖啡...")
    await asyncio.sleep(2)
    print("☕ 咖啡好了！")
    return "咖啡"

async def checkout():
    print("💰 结账中...")
    await asyncio.sleep(1)
    print("💰 结账完成！")
    return "账单"

async def main(): # async 定义的函数会返回一个协程对象，让等待的代码可以继续执行
    start = time.time()
    # 3. 使用 await 调用异步函数
    changfen = await make_changfen() # 等待肠粉做好,await 会等待函数执行完成并返回结果
    coffee = await make_coffee() # 等待咖啡做好,await 会等待函数执行完成并返回结果
    bill = await checkout() # 等待结账完成,await 会等待函数执行完成并返回结果
    
    print(f"\n总共耗时: {time.time() - start:.1f} 秒")

async def main_fast():
    start = time.time()
    changfen,coffee,bill = await asyncio.gather(
        make_changfen(),
        make_coffee(),
        checkout()
    )
    print(f"\n总共耗时: {time.time() - start:.1f} 秒")
# asyncio.run(main_fast())

# 我的作业
# 任务A: 从数据库查用户（模拟2秒）
async def get_user():
    print("👤 开始查用户...")
    await asyncio.sleep(2)
    print("👤 用户查完了！")
    return "用户"

# 任务B: 从API查天气（模拟3秒）  
async def get_weather():
    print("🌤 开始查天气...")
    await asyncio.sleep(3)
    print("🌤 天气查完了！")
    return "天气"

# 任务C: 发送通知    （模拟1秒，但需要用户信息 → 依赖A的结果）
async def send_notification(user):
    print("💬 开始发送通知...")
    await asyncio.sleep(1)
    print("💬 通知发送完了！")
    return "通知"

async def main_task():
    start = time.time()
    user = await get_user()
    weather,notification = await asyncio.gather(get_weather(),send_notification(user))
    print(f"\n总共耗时: {time.time() - start:.1f} 秒")
    print(f"用户: {user}")
    print(f"天气: {weather}")
    print(f"通知: {notification}")

async def main_best():
    start = time.time()
    user,weather = await asyncio.gather(get_user(),get_weather())
    notification = await send_notification(user)
    print(f"\n总共耗时: {time.time() - start:.1f} 秒")
    print(f"用户: {user}")
    print(f"天气: {weather}")
    print(f"通知: {notification}")

async def main_task_version():
    start = time.time()
    # 提前点火,让查用户先跑
    user_task = asyncio.create_task(get_user())
    # 不等他，去查天气
    weather = await get_weather()
    # 等天气查完了，用户也快好了
    user = await user_task
    # 等用户查完了，发送通知
    notification = await send_notification(user)
    print(f"\n总共耗时: {time.time() - start:.1f} 秒")

asyncio.run(main_task_version())