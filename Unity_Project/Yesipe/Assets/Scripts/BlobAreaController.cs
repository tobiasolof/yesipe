using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

public class BlobAreaController : MonoBehaviour
{
    public Vector3 targetPos;
    Vector3 refPos;
    public bool disablePaning, panWithForce;

    public float canvasScaleFactor;

    BlobController[] blobs;

    void Start()
    {
        targetPos = transform.position;
        blobs = GetComponentsInChildren<BlobController>();
        canvasScaleFactor = GetComponentInParent<Canvas>().transform.localScale.x;
    }

    void Update()
    {
        if(!panWithForce)
            transform.position = Vector3.SmoothDamp(transform.position, targetPos, ref refPos, 0.3f);
    }

    public void PanBlobs(Vector2 move)
    {
        if (disablePaning)
        {
            return;
        }

        if (panWithForce)
        {
            move = move / Screen.width * 30000f;

            foreach (var blob in blobs)
            {
                blob.rigidBody2D.AddForce(move);
            }
        }

        targetPos += (Vector3)move / Screen.width * 30f;
    }

    public void PanBlobs(BaseEventData eventData)
    {
        PointerEventData pointerEventData = eventData as PointerEventData;
        PanBlobs(pointerEventData.delta);
    }
}