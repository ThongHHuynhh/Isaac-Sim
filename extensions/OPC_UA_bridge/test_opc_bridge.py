import asyncio
from asyncua import Client


async def main():
    endpoint = "opc.tcp://192.168.122.147:4840"

    print(f"Connecting to {endpoint}")

    async with Client(url=endpoint) as client:
        print("Connected successfully")

        namespaces = await client.get_namespace_array()

        for index, namespace in enumerate(namespaces):
            print(f"{index}: {namespace}")

        print("\nObjects:")

        children = await client.nodes.objects.get_children()

        for child in children:
            browse_name = await child.read_browse_name()
            print(child.nodeid, browse_name)


if __name__ == "__main__":
    asyncio.run(main())