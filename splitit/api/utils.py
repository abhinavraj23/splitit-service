from api.models import *


def isNull(obj):
    return obj is None


def minimumSpaningTree(group_transaction_objs):
    return "abc"


def addToGroupTransactions(amount, debtor_obj, bill_obj):
    payer_obj = bill_obj.payer
    group_obj = bill_obj.group

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

        transaction_obj.amount += amount
        transaction_obj.save()

    else:

        has_owed = GroupTransaction.objects.filter(
            group=group_obj, payer=debtor_obj, debtor=payer_obj).exists()

        if has_owed:
            transaction_obj = GroupTransaction.objects.get(
                group=group_obj, payer=debtor_obj, debtor=payer_obj)

            previous_transaction_amount = transaction_obj.amount

            if previous_transaction_amount == amount:
                transaction_obj.delete()

            elif previous_transaction_amount > amount:
                transaction_obj.amount = previous_transaction_amount - amount
                transaction_obj.save()

            else:
                transaction_obj.delete()
                GroupTransaction.objects.create(
                    group=group_obj, payer=payer_obj, debtor=debtor_obj, amount=amount-previous_transaction_amount)

        else:

            GroupTransaction.objects.create(
                group=group_obj, payer=payer_obj, debtor=debtor_obj, amount=amount)
