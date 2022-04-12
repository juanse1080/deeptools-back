# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from jLmiRvJSeJwBagcoHJsTwqnQUTvwhAxp import protobuf_pb2 as jLmiRvJSeJwBagcoHJsTwqnQUTvwhAxp_dot_protobuf__pb2


class ServerStub(object):
    """----------- Server service ------------

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.execute = channel.unary_stream(
                '/jlmirvjsejwbagcohjstwqnqutvwhaxp.Server/execute',
                request_serializer=jLmiRvJSeJwBagcoHJsTwqnQUTvwhAxp_dot_protobuf__pb2.In.SerializeToString,
                response_deserializer=jLmiRvJSeJwBagcoHJsTwqnQUTvwhAxp_dot_protobuf__pb2.Return.FromString,
                )


class ServerServicer(object):
    """----------- Server service ------------

    """

    def execute(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'execute': grpc.unary_stream_rpc_method_handler(
                    servicer.execute,
                    request_deserializer=jLmiRvJSeJwBagcoHJsTwqnQUTvwhAxp_dot_protobuf__pb2.In.FromString,
                    response_serializer=jLmiRvJSeJwBagcoHJsTwqnQUTvwhAxp_dot_protobuf__pb2.Return.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'jlmirvjsejwbagcohjstwqnqutvwhaxp.Server', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Server(object):
    """----------- Server service ------------

    """

    @staticmethod
    def execute(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/jlmirvjsejwbagcohjstwqnqutvwhaxp.Server/execute',
            jLmiRvJSeJwBagcoHJsTwqnQUTvwhAxp_dot_protobuf__pb2.In.SerializeToString,
            jLmiRvJSeJwBagcoHJsTwqnQUTvwhAxp_dot_protobuf__pb2.Return.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
