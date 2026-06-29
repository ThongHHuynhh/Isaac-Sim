//using System;
//using ABB.Robotics.Controllers;
//using ABB.Robotics.Controllers.Discovery;

//class Program
//{
//    static void Main()
//    {
//        Console.WriteLine("Starting ABB scan...");

//        NetworkScanner scanner = new NetworkScanner();
//        scanner.Scan();

//        Console.WriteLine("Controllers found: " + scanner.Controllers.Count);

//        foreach (ControllerInfo c in scanner.Controllers)
//        {
//            Console.WriteLine("Found: " + c.SystemName);
//        }

//        Console.WriteLine("Press ENTER to exit...");
//        Console.ReadLine();
//    }
//}