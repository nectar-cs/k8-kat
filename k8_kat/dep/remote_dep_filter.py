from functools import reduce
from typing import List, Tuple

from helpers.kube_broker import broker
from k8_kat.dep.kat_dep import KatDep

class RemoteDepFilter:

  @staticmethod
  def and_to_exp(_tuple: Tuple[str, str], eq):
    key, value = _tuple[0], _tuple[1]
    eq_op_sign = "=" if eq == 'yes' else "!="
    return f"{key}{eq_op_sign}{value}"

  @staticmethod
  def or_set_to_exp(_tuple: Tuple[str, List[str]], sign) -> str:
    csv = ", ".join(_tuple[1])
    eq_op = 'in' if sign == 'yes' else 'not in'
    return f"{_tuple[0]} {eq_op} ({csv})"

  @staticmethod
  def ands_to_exps(ands: List[Tuple[str, str]], sign) -> [str]:
    return [me.and_to_exp(and_dict, sign) for and_dict in ands]

  @staticmethod
  def ors_to_exp(ors: List[Tuple[str, str]], sign) -> [str]:
    all_keys = [or_tup[0] for or_tup in ors]

    def agg(whole, key) -> Tuple[str, List[str]]:
      match_tups = [tup for tup in ors if tup[0] == key]
      match_values = [tup[1] for tup in match_tups]
      return whole + [(key, match_values)]

    or_sets = reduce(agg, set(all_keys), [])
    return [me.or_set_to_exp(or_tup, sign) for or_tup in or_sets]

  @staticmethod
  def assemble_expr_lists(total: List[List[str]]):
    pure = [sub_list for sub_list in total if len(sub_list) > 0]
    macro = [','.join(sub_list) for sub_list in pure]
    return ', '.join(macro)

  @staticmethod
  def label_conditions_to_expr(**kwargs):
    and_yes_labels: List[Tuple[str, str]] = kwargs['and_yes_labels']
    and_no_labels: List[Tuple[str, str]] = kwargs['and_no_labels']
    or_yes_labels: List[Tuple[str, str]] = kwargs['or_yes_labels']
    or_no_labels: List[Tuple[str, str]] = kwargs['or_no_labels']

    and_yes_exprs = me.ands_to_exps(and_yes_labels, 'yes')
    and_no_exprs = me.ands_to_exps(and_no_labels, 'no')

    or_yes_exprs = me.ors_to_exp(or_yes_labels, 'yes')
    or_no_exprs = me.ors_to_exp(or_no_labels, 'no')

    return me.assemble_expr_lists([
      and_yes_exprs,
      and_no_exprs,
      or_yes_exprs,
      or_no_exprs
    ])

  @staticmethod
  def fetch_single_namespace(namespace):
    api = broker.appsV1Api
    raw_items = api.list_namespaced_deployment(
      namespace=namespace
    ).items
    return [KatDep(item) for item in raw_items]

  @staticmethod
  def fetch_poly_namespace():
    api = broker.appsV1Api
    raw_items = api.list_deployment_for_all_namespaces().items
    return [KatDep(item) for item in raw_items]


me = RemoteDepFilter
