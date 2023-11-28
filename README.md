# Book Recommender 
Book recommendation system using Deep Learning

## Project topic
Recommendation systems can be found in almost every area of life, from shopping on marketplaces to choosing a TV show for the weekend. 
We wanted to study the topic of recommendations in more detail, understand the work of various methods and create our own recommendation system for books. 
The goal of our project is to study and develop a hybrid book recommendation system.

## Dataset
To train and evaluate our systems, we used the open [goodbooks-10k](https://github.com/zygmuntz/goodbooks-10k) dataset, consisting of 10000 books, 53424 users and 6 million ratings. 
The description and analysis of the data can be found in the 1.0-initial_data_exploration.ipynb

## Demo
![](figures/demo.gif)

[Full demo video](https://drive.google.com/file/d/16WNmHHeeOHjvKeEKwjL5OXO3IxJCNzvT/view?usp=sharing) with good quality

## Models Comparison
|                          | Simple CF | Content-based system | User-based CF using DL | Hybrid model | Fine-tuned hybrid model |
|--------------------------|-----------|----------------------|------------------------|--------------|-------------------------|
| RMSE                     |  3.53569  |       0.95774        |        0.98924         |    0.89941   |       **0.87325**       |
| RMSE for high-rated data |    ---    |       0.89935        |        0.81974         |    0.76834   |       **0.74349**       |

## How to use
### First option: use the telegram bot 
[https://t.me/ultimate_book_recommender_bot](https://t.me/ultimate_book_recommender_bot)

### Second option: run the bot locally
1. Clone the repository

2. Install the required packages
```
pip install -r requirements.txt
```

3. Run the bot
```
python bot.py
```
