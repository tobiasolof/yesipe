using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;

public class YesipeBackendProvider : MonoBehaviour
{
    Suggestions suggestions;
    
    void Start()
    {
        suggestions = GetSuggestion();
    }

    Suggestions GetSuggestion()//string[] chosen) //unkown parameters as of now..
    {
        string url = "localhost:8005/generate_suggestions";
        Suggestions tempSuggestions = new Suggestions();
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);

        return tempSuggestions;
    }
}

public class Suggestions
{
    public List<Suggestion> suggestions;
}
public class Suggestion
{
    public string name;
    public float score;
    public float x;
    public float y;
}