from typing import List

from kubernetes.client import V1Service, V1Pod

from helpers.kube_broker import broker
from k8_kat.dep.dep_collection import DepCollection
from k8_kat.dep.kat_dep import KatDep


class DepComposer:

  @staticmethod
  def svcs_for_dep_coll(dep_coll: DepCollection) -> List[V1Service]:
    api = broker.coreV1
    if dep_coll.query.is_single_ns():
      ns = dep_coll.query.namespace
      return api.list_namespaced_service(namespace=ns).items
    else:
      return api.list_service_for_all_namespaces().items

  @staticmethod
  def pods_for_dep_coll(dep_coll: DepCollection) -> List[V1Pod]:
    api = broker.coreV1
    if dep_coll.query.is_single_ns():
      ns = dep_coll.query.namespace
      return api.list_namespaced_pod(namespace=ns).items
    else:
      return api.list_pod_for_all_namespaces().items

  @staticmethod
  def associate_svcs(dep_coll: DepCollection) -> [KatDep]:
    raw_svcs = DepComposer.svcs_for_dep_coll(dep_coll)
    DepComposer.zip_candidates(dep_coll, raw_svcs, 'svcs')

  @staticmethod
  def associate_pods(dep_coll: DepCollection) -> [KatDep]:
    raw_pods = DepComposer.pods_for_dep_coll(dep_coll)
    DepComposer.zip_candidates(dep_coll, raw_pods, 'pods')

  @staticmethod
  def zip_candidates(dep_coll: DepCollection, others, method: str):
    for dep in dep_coll.go():
      getattr(dep, f"assoc_{method}")(others)
