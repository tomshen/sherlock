sherlock
========

Wikipedia article question answerer and asker

## Timeline
- ~~Due Monday, February 24: Minimal viable product~~
  * ~~Allie: question asker~~
  * ~~Shoup: question answerer~~
  * ~~Tom: article parser~~
* ~~Due Tuesday, February 25: Progress report 1~~
* Due Tuesday, March 4: Second milestone
 * Can ask grammatically correct questions
 * Can answer all questions it can ask
 * Database contains correct relations, with relation type and certainty
* Due Thursday, March 20: Progress report 2 (**video**)

## Database
```python
{
  "The Artist": {
    "Frenchromantic film": {
      "relation": [('is', 'VBZ'), ...],
      "certainty": 0.9, # a float in the interval (0, 1]
      "sentiment": 0.1, # a float in the interval [-1.0, 1.0]
      "pos": [('Frenchromantic', 'JJ'), ('film', 'NN')]
    },
    .
    .
    .
  },
  .
  .
  .
}
```
