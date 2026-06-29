using ABB.Robotics.Controllers;
using ABB.Robotics.Controllers.Discovery;
using ABB.Robotics.Controllers.MotionDomain;
using ABB.Robotics.Controllers.RapidDomain;
using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;

class IsaacBridge
{
    static void Main()
    {
        //IP and port constant
        string isaacIp = "10.89.1.85";
        int isaacPort = 5000;

        //Create scanner object
        NetworkScanner scanner = new NetworkScanner();
        scanner.Scan();

        if (scanner.Controllers.Count == 0)
        {
            Console.WriteLine("No controllers found.");
            Console.ReadLine();
            return;
        }

        // Connect to the first robot it found
        ControllerInfo info = scanner.Controllers[0];
        Console.WriteLine("Connecting to: " + info.SystemName);

        using (Controller controller = ControllerFactory.CreateFrom(info))
        //Open TCP Connection to Isaac Computer at 10.89.1.85 on port 5000
        using (TcpClient client = new TcpClient(isaacIp, isaacPort))
        //Open a stream to push data through
        using (NetworkStream stream = client.GetStream())
        {
            // Login to the robot using default creds
            controller.Logon(UserInfo.DefaultUser);
            Console.WriteLine("Logged in.");
            Console.WriteLine("Connected to Isaac TCP.");

            MechanicalUnit mech = controller.MotionSystem.MechanicalUnits[0];
            // Print out Robot Name
            Console.WriteLine("Mechanical Unit: " + mech.Name);

            while (true)
            {
                // Get joint value from Mech
                JointTarget jt = mech.GetPosition();

                // Convert position to json string
                string json =
                    $"{{\"joints\":[{jt.RobAx.Rax_1:F4},{jt.RobAx.Rax_2:F4},{jt.RobAx.Rax_3:F4},{jt.RobAx.Rax_4:F4},{jt.RobAx.Rax_5:F4},{jt.RobAx.Rax_6:F4}]}}\n";

                byte[] data = Encoding.UTF8.GetBytes(json);
                
                // Sending data, start from 0 -> end of data
                stream.Write(data, 0, data.Length);

                Console.WriteLine(json.Trim());

                //Pause the program 20ms -> 50hz
                Thread.Sleep(10);
            }
        }
    }
}