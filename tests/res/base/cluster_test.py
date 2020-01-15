from k8_kat.utils.testing.fixtures import test_env
from tests.res.base.k8_kat_test import K8KatTest


class ClusterTest(K8KatTest):

  @staticmethod
  def ensure_no_pods(namespaces=None):
    pass

  @classmethod
  def setUpClass(cls) -> None:
    super(ClusterTest, cls).setUpClass()
    test_env.cleanup()
    test_env.create_namespaces()

  @classmethod
  def tearDownClass(cls):
    pass