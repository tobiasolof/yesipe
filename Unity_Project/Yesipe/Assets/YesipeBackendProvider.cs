//using System;
//using System.Collections;
//using System.Collections.Generic;
//using UnityEngine;
//using System.Net;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using UnityEngine.Networking;

public class YesipeBackendProvider : MonoBehaviour
{
    public BlobController blobPrefab;
    List<BlobController> oldBlobs = new List<BlobController>();
    List<BlobController> newBlobs = new List<BlobController>();

    [SerializeField]
    Suggestions suggestions;

    string POSTUrl = "localhost:8005/generate_suggestions";
    public string POSTBody;

    YesipeColors colors;

    private void Awake()
    {
        colors = GetComponent<YesipeColors>();
        newBlobs.AddRange(GetComponentsInChildren<BlobController>());
    }

    void Start()
    {
        StartCoroutine(UpdateSuggestions(POSTUrl, POSTBody));
    }

    [ContextMenu("UpdateBlobs")]
    void UpdateBlobsFunction()
    {
        StartCoroutine(UpdateBlobs());
    }

    IEnumerator UpdateBlobs()
    {
        if (newBlobs.Count != 0)
        {
            oldBlobs = newBlobs;
            newBlobs = new List<BlobController>();
        }

        foreach (var blob in oldBlobs)
        {
            //float angle = ConversionMethods.CartesianToPolar(blob.transform.position).x;
            //blob.SetTargetPosition(ConversionMethods.PolarToCartesian(UnityEngine.Random.Range(0f, 360f), 20), true);
            blob.SetTargetPosition(blob.transform.position.normalized * 20f, true, 2f);
        }

        yield return new WaitForSeconds(.5f);

        foreach (var item in suggestions.suggestions)
        {
            BlobController newBlob = Instantiate(blobPrefab, transform);
            newBlobs.Add(newBlob);
            //newBlob.transform.position = new Vector2(UnityEngine.Random.Range(-10f, 10f), UnityEngine.Random.Range(-10f, 10f));
            newBlob.transform.position = ConversionMethods.PolarToCartesian(UnityEngine.Random.Range(0f, 360f), 20);
            newBlob.SetTitle(item.name);
            newBlob.color = colors.bubbleColors[UnityEngine.Random.Range(0, colors.bubbleColors.Length)];
            newBlob.SetTargetPosition(new Vector2(), false, UnityEngine.Random.Range(0.5f, 1f));
            //newBlob.SetTargetPosition(new Vector2(UnityEngine.Random.Range(-10f, 10f), UnityEngine.Random.Range(-10f, 10f)), false, 0.5f);
        }
    }

    IEnumerator UpdateSuggestions(string url, string bodyJsonString)
    {
        var request = new UnityWebRequest(url, "POST");
        byte[] jsonRaw = Encoding.UTF8.GetBytes(bodyJsonString);
        request.uploadHandler = new UploadHandlerRaw(jsonRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        Debug.Log("Status Code: " + request.responseCode);

        string response = Encoding.UTF8.GetString(request.downloadHandler.data);
        response = "{\"suggestions\":" + response + "}";

        print(response);

        suggestions = JsonUtility.FromJson<Suggestions>(response);

        StartCoroutine(UpdateBlobs());
    }

    
}

[Serializable]
public class Suggestions
{
    public List<Suggestion> suggestions;
}
[Serializable]
public class Suggestion
{
    public string name;
    public float score;
    public float x;
    public float y;
}