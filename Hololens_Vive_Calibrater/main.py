"""This module is the entry point to the  holo-vive-calibration process wherein
    the lighthouse system and virtual center of hte hololens are calibrated towards one another
    or rather the tracker and the virtual center

    This is basically implemented as a consumer/producer pattern

    A tcp/ip server acts as the producer as it accepts points fromt he hololens
    these are bundled and put into a queue

    The quue is consumed via a pipeline which a "pipeline". Therein it is attempted to 
    find the transformation. The following steps are applied
        1. get information about both tracker calibration_tracker and hololens_tracker via gRPC
        2. access the received hololens message for correctness as in check if it conforms to the agreed message pattern
        3. use the rotation+translation of the calibration tracker which is attached to the calirbation object to find the 3D points to match
        4. get the virtual points to match against the 3D points
        5. Push these point sets consisting of point correspondances to the point register container 
        6. Await the resulting transformation
        7. Apply it together with the transformation of the tracker to get the transformation from tracker to virtual center
    """
import asyncio


from loguru import logger

from modules.worker import worker
from modules.communication.async_tcp_ip_server import TcpIPServer
from config.const import TCP_HOST, TCP_PORT


async def main():
    queue = asyncio.Queue()
    tcp_host = TCP_HOST
    tcp_port = TCP_PORT
    tcp_server = TcpIPServer(IP=tcp_host, port=tcp_port, queue=queue)
    await asyncio.gather(tcp_server.start(), worker(queue))

if __name__ == "__main__":
    logger.info("Starting HoloCalibration Service")

    asyncio.run(main())
