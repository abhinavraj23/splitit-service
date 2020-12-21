from api.models import *
import heapq
from collections import defaultdict


def isNull(obj):
    return obj is None


def minimize_transaction(group_transaction_objs):
    # transactions are tubbles with (from, to, amount)
    # do all transaction which gives the net_flow to and from each friends

    net_flow = defaultdict(float)
    for group_transaction_obj in group_transaction_objs:
        net_flow[str(group_transaction_obj.payer.username)
                 ] -= float(group_transaction_obj.amount)
        net_flow[str(group_transaction_obj.debtor.username)
                 ] += float(group_transaction_obj.amount)

    # negatives and positives are min-heaps to be populated
    negatives = []
    positives = []
    for user_id, amount in net_flow.items():
        if amount < 0:
            heapq.heappush(negatives, (amount, user_id))
        elif amount > 0:
            # python has a min heap per default...
            heapq.heappush(positives, (-amount, user_id))

    settlement = []
    # optimize the flow using the two heaps
    while positives and negatives:

        pos = heapq.heappop(positives)
        neg = heapq.heappop(negatives)
        amount = max(pos[0], neg[0])  # are both negative values

        temp = {}
        temp['payer'] = str(neg[1])
        temp['debtor'] = str(pos[1])
        temp['amount'] = str(-amount)
        settlement.append(temp)

        if pos[0] - amount < 0:
            heapq.heappush(positives, (pos[0] + amount, pos[1]))
        elif neg[0] - amount < 0:
            heapq.heappush(negatives, (neg[0] + amount, neg[1]))

    return settlement


def addToGroupTransactions(amount, payer_obj, debtor_obj, group_obj):
    '''
    let payer = A, debtor = B
    Here we are checking if in the group any of the following scenarios are present:

    1) A -has paid for-> B (i.e. A has paid)
    2) B -has paid for-> A (i.e A has owed)

    else if no previous transaction is present, simply we will add a new group transaction

    '''

    has_paid = GroupTransaction.objects.filter(
        group=group_obj, payer=payer_obj, debtor=debtor_obj).exists()

    if has_paid:
        transaction_obj = GroupTransaction.objects.get(
            group=group_obj, payer=payer_obj, debtor=debtor_obj)


        transaction_amount = float(transaction_obj.amount)
        transaction_amount += amount
        transaction_obj.amount = transaction_amount
        transaction_obj.save()

    else:

        has_owed = GroupTransaction.objects.filter(
            group=group_obj, payer=debtor_obj, debtor=payer_obj).exists()

        if has_owed:
            transaction_obj = GroupTransaction.objects.get(
                group=group_obj, payer=debtor_obj, debtor=payer_obj)

            previous_transaction_amount = float(transaction_obj.amount)

            if previous_transaction_amount == amount:
                transaction_obj.delete()

            elif previous_transaction_amount > amount:
                transaction_amount = float(transaction_obj.amount)
                transaction_amount = previous_transaction_amount - amount
                transaction_obj.amount = transaction_amount
                transaction_obj.save()

            else:
                transaction_obj.delete()
                GroupTransaction.objects.create(
                    group=group_obj, payer=payer_obj, debtor=debtor_obj, amount=amount-previous_transaction_amount)

        else:

            GroupTransaction.objects.create(
                group=group_obj, payer=payer_obj, debtor=debtor_obj, amount=amount)
