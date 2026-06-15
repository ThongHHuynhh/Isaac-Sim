import omni.usd
import omni.kit.commands
import asyncio

stage = omni.usd.get_context().get_stage()

product_path = "/World/Pan"

async def spawn_loop():
    counter = 0
    while True:
        new_path = f"/World/Product_{counter}"

        omni.kit.commands.execute(
            "CopyPrim", 
            path_from=product_path,
            path_to=new_path
        )
        print(f"Spawned {new_path}")

        counter +=1

        await asyncio.sleep(1.0)

asyncio.ensure_future(spawn_loop())

# import asyncio

# for task in asyncio.all_tasks():
#     print(task)
#     task.cancel()