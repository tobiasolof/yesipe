using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[ExecuteAlways]
public class BlobShaderHelper : MonoBehaviour
{
    public Material material;
    //RectTransform rect;
    
    void Start()
    {
        //rect = GetComponent<RectTransform>();
    }

    void Update()
    {
        material.SetVector("ObjectPosition", transform.position);
    }
}
