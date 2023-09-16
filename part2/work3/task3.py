import random
from typing import NamedTuple
from typing import Iterable

import reactivex
from reactivex import operators as ops


class UserFriend(NamedTuple):
    user_id: int
    friend_id: int


class UserManager:
    def __init__(self, users_friends: list[UserFriend]):
        self.users_friends = users_friends

    def get_friends_stream(self, user_id: int):
        return reactivex.from_iterable(self.users_friends).pipe(
            ops.filter(lambda rel: rel.user_id == user_id)
        )

    def get_users_friends_stream(self, users_ids: Iterable[int]):
        return reactivex.from_iterable(users_ids).pipe(
            ops.map(lambda user_id: self.get_friends_stream(user_id)),
            ops.flat_map(lambda rel: rel)
        )


def generate_users_friends(users_ids: list[int]) -> list[UserFriend]:
    users_friends: list[UserFriend] = []

    for user_id in users_ids:
        friends_ids = set(users_ids)

        for _ in range(random.randint(0, len(users_ids))):
            friend_id = random.choice(list(friends_ids))
            users_friends.append(
                UserFriend(
                    user_id=user_id,
                    friend_id=friend_id,
                )
            )

            friends_ids.remove(friend_id)

    return users_friends


def main():
    print_user_friend = lambda user_friend: print(f"{user_friend.user_id} -> {user_friend.friend_id}")

    users_ids = list(range(1, 5))
    users_friends = generate_users_friends(users_ids=users_ids)
    random.shuffle(users_ids)

    for user_friend in users_friends:
        print_user_friend(user_friend)

    required_users_ids = users_ids[:random.randint(1, len(users_ids))]
    print("required users ids:", required_users_ids)

    user_manager = UserManager(users_friends=users_friends)

    stream = user_manager.get_users_friends_stream(users_ids=users_ids)
    stream.subscribe(on_next=print_user_friend)


if __name__ == "__main__":
    main()
