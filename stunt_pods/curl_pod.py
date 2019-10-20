import re
from utils.utils import Utils

from helpers.kube_broker import broker
from stunt_pods.stunt_pod import StuntPod

HEADER_BODY_DELIM = "\r\n\r\n"

class CurlPod(StuntPod):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.pod_name = kwargs.get('pod_name', f"curl-pod-{Utils.rand_str(4)}")
    self.exec_command = CurlPod.build_cmd(**kwargs)

  def run(self):
    result = super().run()
    if result is not None:
      result = CurlPod.parse_response(result)
    return result

  @staticmethod
  def build_cmd(**kwargs):
    command = kwargs.get('command')
    if command:
      return command.split(" ")
    else:
      return CurlPod.build_curl_cmd(**kwargs)

  @staticmethod
  def build_curl_cmd(**params):
    raw_headers = params.get('headers', {})
    headers = [f"{0}: {1}".format(k, v) for k, v in raw_headers]
    body = params.get('body', None)

    cmd = [
      "curl",
      "-s",
      "-i",
      '-X', params.get('verb', 'GET'),
      '-H', headers,
      '-d' if body else None, body if body else None,
      "--connect-timeout", "1",
      params['url']
    ]
    return list(filter(lambda p: p is not None, cmd))

  @staticmethod
  def parse_status(header):
    out = re.search('HTTP/(\d*)\.(\d*) (\d*) .*', header)
    return out.group(3)

  @staticmethod
  def parse_response(response):
    if response:
      parts = response.split(HEADER_BODY_DELIM)
      headers = parts[0].split("\r\n")
      body_parts = parts[1:len(parts)]
      body = body_parts[0]

      return {
        "raw": response,
        "headers": headers,
        "body": body,
        "status": CurlPod.parse_status(headers[0]),
        "finished": True
      }
    else:
      return CurlPod.format_empty_response()

  @staticmethod
  def format_empty_response():
    return {
      "raw": "N/A",
      "headers": ["N/A"],
      "body": "Could not connect",
      "status": "N/A",
      "finished": False
    }

  @staticmethod
  def cleanup():
    victims = broker.coreV1.list_pod_for_all_namespaces(
      label_selector='nectar-type=stunt-pod'
    ).items

    names = []
    for pod in victims:
      names.append(pod.metadata.name)
      broker.coreV1.delete_namespaced_pod(
        name=pod.metadata.name,
        namespace=pod.metadata.namespace
      )
    return len(names)

  @staticmethod
  def play():
    curler = CurlPod(
      pod_name="curl-man",
      delete_after=False,
      url="10.0.20.109:80"
    )
    out = curler.run()
    print(out['status'])
