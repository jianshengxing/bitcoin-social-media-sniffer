#!/usr/bin/python3

import asyncio
import websockets
import binascii
import ujson as json
import argparse

memo_method_map = {
  '6d01': 'Set Name',
  '6d02': 'Post',
  '6d03': 'Reply',
  '6d04': 'Like/Tip',
  '6d05': 'Set Profile',
  '6d06': 'Follow',
  '6d07': 'Unfollow',
  '6d0c': 'Topic Message'
}

blockpress_method_map = {
  '8d01': 'Set Name',
  '8d02': 'Post',
  '8d03': 'Reply',
  '8d04': 'Like/Tip',
  '8d06': 'Follow',
  '8d07': 'Unfollow',
  '8d08': 'Set Profile Header',
  '8d09': 'Create Media Post',
  '8d10': 'Set Profile Avatar',
  '8d11': 'Creat Post in Community',
}

async def client_loop(method_map):
  async with websockets.connect('wss://ws.blockchain.info/bch/inv') as websocket:
    await websocket.send('{"op":"unconfirmed_sub"}')
    while True:
      message = await websocket.recv()
      payload = json.loads(message)
      data = payload['x']
      outputs = data['out']
      for output in outputs:
          if output['script'].startswith('6a02'):
              print("----------")
              print('TX: {}'.format(data['hash']))
              print('Script: {}'.format(output['script']))
              method = output['script'][4:8]
              if method not in method_map:
                  #print('Incompatible Operation')
                  continue
              if method_map[method] == 'Post':
                  message = output['script'][10:]
                  print('New post: {}'.format(binascii.unhexlify(message)))
              elif method_map[method] == 'Reply':
                  rts = output['script'][10:74]
                  reply_to = "".join(reversed([rts[i:i+2] for i in range(0, len(rts), 2)]))
                  reply_len = output['script'][74:76]
                  reply_msg = output['script'][76:]
                  print('To: {}'.format(reply_to))
                  print('Length: {}'.format(reply_len))
                  print('Message: {}'.format(binascii.unhexlify(reply_msg)))
              else:
                  print('Action {} > {}'.format(method_map[method], output['script'][10:]))

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-m", "--memo", help="Sniff Memo.cash actions", action="store_true")
group.add_argument("-b", "--blockpress", help="Sniff BlockPress.com actions", action="store_true")
args = parser.parse_args()

if args.memo:
    asyncio.get_event_loop().run_until_complete(client_loop(memo_method_map))
elif args.blockpress:
    asyncio.get_event_loop().run_until_complete(client_loop(blockpress_method_map))

