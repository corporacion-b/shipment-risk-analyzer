from src.repositories.alert_repository import AlertRepository


def test_list_for_user_excludes_dismissed_alerts(monkeypatch):
    repository = AlertRepository()
    queries = []

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def execute(self, query, params=None):
            queries.append(query)

        def fetchall(self):
            return []

        def fetchone(self):
            return {"total": 0}

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def cursor(self):
            return Cursor()

    monkeypatch.setattr("src.repositories.alert_repository.database.connect", lambda: Connection())

    repository.list_for_user(1)

    assert all("DISMISSED" in query for query in queries)


def test_dismiss_for_user_marks_alert_dismissed(monkeypatch):
    repository = AlertRepository()
    executed = {}

    class Cursor:
        rowcount = 1

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def execute(self, query, params=None):
            executed["query"] = query
            executed["params"] = params

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def cursor(self):
            return Cursor()

    monkeypatch.setattr("src.repositories.alert_repository.database.connect", lambda: Connection())

    dismissed = repository.dismiss_for_user(10, 1)

    assert dismissed == 1
    assert "SET status = 'DISMISSED'" in executed["query"]
    assert executed["params"] == (10, 1)


def test_alert_exists_counts_dismissed_alerts(monkeypatch):
    repository = AlertRepository()
    executed = {}

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def execute(self, query, params=None):
            executed["query"] = query
            executed["params"] = params

        def fetchone(self):
            return {"total": 1}

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def cursor(self):
            return Cursor()

    monkeypatch.setattr("src.repositories.alert_repository.database.connect", lambda: Connection())

    exists = repository.alert_exists(1, "ABC123", "SHIPMENT_EXCEPTION", "Exception")

    assert exists is True
    assert "DISMISSED" not in executed["query"]
