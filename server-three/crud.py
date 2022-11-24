class CRUD:

  @staticmethod
  def create(data_set, key, value):
    data_set[key] = value
    return "success"

  @staticmethod
  def read(data_set, key):
    # print(data_set.get(key))
    return data_set.get(key)

  @staticmethod
  def update(data_set, key, value):
    data_set.update({key: value})
    return "success"

  @staticmethod
  def delete(data_set, key):
    data_set.pop(key)
    return "success"
