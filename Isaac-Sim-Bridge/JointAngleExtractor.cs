//using System;
//using System.Threading;
//using ABB.Robotics.Controllers;
//using ABB.Robotics.Controllers.Discovery;
//using ABB.Robotics.Controllers.MotionDomain;
//using ABB.Robotics.Controllers.RapidDomain;
//class JointAngleExtractor
//{
//    static void Main()
//    {
//        NetworkScanner scanner = new NetworkScanner();
//        scanner.Scan();

//        Console.WriteLine("Controllers found: " + scanner.Controllers.Count);

//        ControllerInfo info = scanner.Controllers[0];
//        Console.WriteLine("Connecting to: " + info.SystemName);

//        using (Controller controller = ControllerFactory.CreateFrom(info))
//        {
//            controller.Logon(UserInfo.DefaultUser);
//            Console.WriteLine("Logged in.");

//            MechanicalUnit mech = controller.MotionSystem.MechanicalUnits[0];
//            Console.WriteLine("Mechanical Unit: " + mech.Name);

//            while (true)
//            {
//                JointTarget jt = mech.GetPosition();

//                Console.WriteLine(
//                    $"Joints: \n" +
//                    $"J1: {jt.RobAx.Rax_1:F2}\n" +
//                    $"J2: {jt.RobAx.Rax_2:F2}\n" +
//                    $"J3: {jt.RobAx.Rax_3:F2}\n" +
//                    $"J4: {jt.RobAx.Rax_4:F2}\n" +
//                    $"J5: {jt.RobAx.Rax_5:F2}\n" +
//                    $"J6: {jt.RobAx.Rax_6:F2}\n");

//                Thread.Sleep(20);
//            };
//        }
//    }
//}