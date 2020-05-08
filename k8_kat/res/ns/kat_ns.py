from typing import Callable, Dict

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.relation.relation import Relation
from k8_kat.res.sa.kat_service_account import KatServiceAccount
from k8_kat.utils.main.class_property import classproperty


class KatNs(KatRes):

  @classproperty
  def kind(self):
    return "Namespace"

  def _perform_delete_self(self):
    broker.coreV1.delete_namespace(self.name)

  def is_active(self) -> bool:
    if self.raw.status:
      return self.raw.status.phase == 'Active'
    else:
      return False

  def is_work_ready(self) -> bool:
    if self.is_active():
      default_sa = KatServiceAccount.find('default', self.name)
      if default_sa:
        if len(default_sa.secrets()) == 1:
          return None not in default_sa.secrets()
    return False

# --
# --
# --
# -------------------------------PLUMBING-------------------------------
# --
# --
# --

  @classmethod
  def is_namespaced(cls) -> bool:
    return False

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_namespace,
      patch=broker.coreV1.patch_namespace,
      delete=broker.coreV1.delete_namespace
    )
