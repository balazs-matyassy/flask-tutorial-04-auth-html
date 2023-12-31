import base64
import os

__recipes_path = 'instance/recipes.txt'


def init_app(app):
    global __recipes_path

    __recipes_path = os.path.join(app.instance_path, 'recipes.txt')


class Recipe:
    def __init__(self, category='', name='', description='', difficulty=1, recipe_id=None):
        self.recipe_id = recipe_id
        self.category = category
        self.name = name
        self.description = description
        self.difficulty = difficulty

    @property
    def difficulty_description(self):
        if self.difficulty == 1:
            return 'Very easy'
        elif self.difficulty == 2:
            return 'Easy'
        elif self.difficulty == 3:
            return 'Medium'
        elif self.difficulty == 4:
            return 'Difficult'
        elif self.difficulty == 5:
            return 'Very difficult'

        return 'Unknown'

    def update(self, data):
        self.category = (data.get('category') or '').strip()
        self.name = (data.get('name') or '').strip()
        self.description = (data.get('description') or '').strip()

        try:
            self.difficulty = int(data.get('difficulty') or 1)

            if self.difficulty < 1:
                self.difficulty = 1
            elif self.difficulty > 5:
                self.difficulty = 5
        except ValueError:
            self.difficulty = 1

    def validate(self):
        errors = []

        if self.category == '':
            errors.append('Category missing.')

        if self.name == '':
            errors.append('Name missing.')

        return errors

    def to_line(self):
        description = (base64
                       .b64encode(self.description.encode('utf-8'))
                       .decode('utf-8'))

        return (
            f'{self.recipe_id}\t{self.category}\t{self.name}'
            f'\t{description}\t{self.difficulty}'
        )

    @staticmethod
    def create_from_line(line):
        values = line.strip().split('\t')
        description = (base64
                       .b64decode(values[3].strip().encode('utf-8'))
                       .decode('utf-8'))

        return Recipe(
            recipe_id=int(values[0].strip()),
            category=values[1].strip(),
            name=values[2].strip(),
            description=description,
            difficulty=int(values[4].strip())
        )


def find_all():
    with open(__recipes_path, encoding='utf-8') as file:
        recipes = []

        file.readline()  # header

        for line in file:
            recipe = Recipe.create_from_line(line)
            recipes.append(recipe)

        return recipes


def find_by_id(recipe_id):
    for recipe in find_all():
        if recipe.recipe_id == recipe_id:
            return recipe

    return None


def find_by_name(name):
    recipes = []

    for recipe in find_all():
        if name.lower() in recipe.name.lower():
            recipes.append(recipe)

    return recipes


def save(recipe):
    recipes = find_all()

    if recipe.recipe_id is None:
        max_id = 0

        for i in range(len(recipes)):
            if recipes[i].recipe_id > max_id:
                max_id = recipes[i].recipe_id

        recipe.recipe_id = max_id + 1
        recipes.append(recipe)
    else:
        for i in range(len(recipes)):
            if recipes[i].recipe_id == recipe.recipe_id:
                recipes[i] = recipe
                break

    __store_all(recipes)

    return recipe


def delete_by_id(recipe_id):
    recipes = find_all()

    for i in range(len(recipes)):
        if recipes[i].recipe_id == recipe_id:
            recipes.pop(i)
            break

    __store_all(recipes)


def __store_all(recipes):
    with open(__recipes_path, 'w', encoding='utf-8') as file:
        file.write('id\tcategory\tname\tdescription\tdifficulty\n')

        for recipe in sorted(recipes, key=lambda item: f'{item.category}\0{item.name}'):
            file.write(f'{recipe.to_line()}\n')
