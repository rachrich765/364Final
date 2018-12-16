(You bold things in Markdown by using two asterisks, like this: **This text would be bold** and this text would not be) and should include a 1-paragraph (brief OK) description of what your application does and have the routes
A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.

1. **Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, like this )**

2. **Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.**

3. **Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).**

4. **Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.**

5. **At least 3 model classes besides the User class.**
	Confusing_Hashtag, PersonalHashtagCollection, ConfusingTweeter

6. **At least one one:many relationship that works properly built between 2 models.**
	PersonalHashtagCollection & Users
	ConfusingTweeter & ConfusingHashtag

 7. **At least one many:many relationship that works properly built between 2 models.**
 	ConfusingHashtag & PersonalHashtagCollection

 8. **Successfully save data to each table.**

 9. **Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).**

 10. **At least one query of data using an .all() method and send the results of that query to a template.**
 	found in . . 
 		/create_collection route 
 		/collection/<title> route 
 		/all_confusing_tweeters 

 11. **At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).**
 	found in. . . 
 		/all_confusing_tweeters 
 		/update/<hashtag> 
 		/delete/<collection> 
 		/collection/<title>
 		/collections
 		get_hashtag_by_id(id)
 		get_or_create_collection(title, current_user, ht_list=[])
 		 get_or_create_hashtag
 
12. **At least one helper function that is not a get_or_create function should be defined and invoked in the application.**
	get_hashtag_by_id(id)
	get_hashtag_defs_from_API

 13. **At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).**
 	get_or_create_hashtag(hashtag, tweeter, difficulty, definition)
 	get_or_create_collection(title, current_user, ht_list=[])

 14. **At least one error handler for a 404 error and a corresponding template.**

 15. **Include at least 4 template .html files in addition to the error handling template files.**

 16. **At least one Jinja template for loop**
 	all_hashtags_and_ct.html
 	collection_contents.html
 	hashtag_results.html
 	personal_collection.html
 17.  **At least two Jinja template conditionals should occur amongst the templates.**
 	all_hashtags_and_ct.html
 	create_collection.html
 
 18. **At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).**

 19. **Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).**
 
 20. **At least one WTForm that sends data with a GET request to a new page.**
 	UpdateButtonForm

21. **At least one WTForm that sends data with a POST request to the same page. (NOT counting the login or registration forms provided for you in class.)**
	HashtagForm

 22. **At least one WTForm that sends data with a POST request to a new page. (NOT counting the login or registration forms provided for you in class.)**
 	CollectionCreateForm

 23. **At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.**
 	validate_difficult(form, field)
 	validate_hashtag(form,field)

24. **Include at least one way to update items saved in the database in the application (like in HW5).**

25. **Include at least one way to delete items saved in the database in the application (also like in HW5).**

26. **Include at least one use of redirect.**
	/create_collection
	/delete/<collection>
	/update/<hashtag>

 27. **Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)**
 	/create_collection
 	/delete/<collection>
 	/update/<hashtag>

 28. **Have at least 5 view functions that are not included with the code we have provided.**